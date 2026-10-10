from datetime import timedelta
import os
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app import create_app
from flask_jwt_extended import create_access_token
from src.config import Config
from src.db import check_db_connection
from src.dev_database import reset_development_database
from src.routes.health import health_check
from src.services.image_service import ImageService, ImageUploadError


class DeploymentConfigTests(unittest.TestCase):
    admin_username = "editorial-owner"
    admin_password = "Secure-editorial-access-2026!"
    jwt_secret = "local-signing-key-with-32-bytes-not-a-placeholder-12345"

    def setUp(self):
        self.ca_file = tempfile.NamedTemporaryFile(suffix=".pem", delete=False)
        self.ca_file.close()
        self.environment = patch.dict(
            os.environ,
            {
                "DB_HOST": "mysql.example.test",
                "DB_PORT": "1234",
                "DB_USER": "app_user",
                "DB_PASSWORD": "test-password",
                "DB_NAME": "app_db",
                "CORS_ORIGINS": "https://codigo-femenino.vercel.app",
                "ADMIN_USERNAME": self.admin_username,
                "ADMIN_PASSWORD": self.admin_password,
                "JWT_SECRET_KEY": self.jwt_secret,
            },
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.addCleanup(os.unlink, self.ca_file.name)

    def production_config(self, **overrides):
        values = {
            "APP_ENV": "production",
            "DEBUG": False,
            "RESET_DEV_DATABASE_ON_STARTUP": False,
            "DB_SSL_REQUIRED": True,
            "DB_SSL_CA": self.ca_file.name,
            "CORS_ORIGINS": ["https://codigo-femenino.vercel.app"],
            "CLOUDINARY_CLOUD_NAME": None,
            "CLOUDINARY_API_KEY": None,
            "CLOUDINARY_API_SECRET": None,
            "ADMIN_USERNAME": self.admin_username,
            "ADMIN_PASSWORD": self.admin_password,
            "JWT_SECRET_KEY": self.jwt_secret,
            "REDIS_URL": "rediss://redis.example.test:6379/0",
            "RATE_LIMIT_STORAGE_URI": "memory://",
        }
        values.update(overrides)
        return patch.multiple(Config, **values)

    def test_production_rejects_wildcard_cors(self):
        with self.production_config(CORS_ORIGINS=["*"]):
            with self.assertRaisesRegex(ValueError, "CORS_ORIGINS"):
                Config.validate()

    def test_production_requires_existing_verified_tls_ca(self):
        with self.production_config(DB_SSL_CA=None):
            with self.assertRaisesRegex(ValueError, "DB_SSL_REQUIRED"):
                Config.validate()

    def test_production_configuration_accepts_explicit_https_origin(self):
        with self.production_config():
            Config.validate()

    def test_production_rejects_partial_database_configuration(self):
        with self.production_config(DB_PASSWORD=None):
            with self.assertRaisesRegex(ValueError, "DB_PASSWORD"):
                Config.validate()

    def test_production_requires_long_jwt_signing_secret(self):
        with self.production_config(JWT_SECRET_KEY="too-short"):
            with self.assertRaisesRegex(ValueError, "JWT_SECRET_KEY"):
                Config.validate()

    def test_production_requires_external_redis_storage(self):
        with self.production_config(REDIS_URL=None):
            with self.assertRaisesRegex(ValueError, "REDIS_URL"):
                Config.validate()
        with self.production_config(REDIS_URL="memory://"):
            with self.assertRaisesRegex(ValueError, "REDIS_URL"):
                Config.validate()

    def test_production_rate_limiter_uses_redis_without_memory_fallback(self):
        redis_url = "rediss://redis.example.test:6379/0"
        with self.production_config(RATE_LIMIT_STORAGE_URI=redis_url):
            app = create_app()

        self.assertEqual(app.config["RATELIMIT_STORAGE_URI"], redis_url)
        self.assertFalse(app.config["RATELIMIT_IN_MEMORY_FALLBACK_ENABLED"])

    def test_production_rejects_example_administrator_credentials(self):
        with self.production_config(ADMIN_USERNAME="admin"):
            with self.assertRaisesRegex(ValueError, "ADMIN_USERNAME"):
                Config.validate()
        with self.production_config(ADMIN_PASSWORD="change-me-example-password"):
            with self.assertRaisesRegex(ValueError, "ADMIN_PASSWORD"):
                Config.validate()
        with self.production_config(
            JWT_SECRET_KEY="your-jwt-signing-key-with-32-bytes-and-example-suffix"
        ):
            with self.assertRaisesRegex(ValueError, "JWT_SECRET_KEY"):
                Config.validate()

    def test_production_requires_a_strong_admin_password(self):
        with self.production_config(ADMIN_PASSWORD="short"):
            with self.assertRaisesRegex(ValueError, "ADMIN_PASSWORD"):
                Config.validate()

    def test_production_debug_cannot_be_enabled_by_environment_variable(self):
        environment = os.environ.copy()
        environment.update(
            {"APP_ENV": "production", "FLASK_DEBUG": "true"}
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.config import Config; assert Config.DEBUG is False",
            ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_production_app_factory_does_not_initialize_database(self):
        with self.production_config():
            with patch("src.dev_database.pymysql.connect") as connect:
                app = create_app()
            self.assertFalse(app.debug)
            connect.assert_not_called()

    def test_production_refuses_database_reset_before_connecting(self):
        with self.production_config(RESET_DEV_DATABASE_ON_STARTUP=True):
            with patch("src.dev_database.pymysql.connect") as connect:
                with self.assertRaisesRegex(RuntimeError, "development"):
                    reset_development_database()
            connect.assert_not_called()

    def test_cloudinary_reports_unconfigured_service_without_credentials(self):
        with patch.multiple(
            Config,
            CLOUDINARY_CLOUD_NAME=None,
            CLOUDINARY_API_KEY=None,
            CLOUDINARY_API_SECRET=None,
        ):
            with self.assertRaises(ImageUploadError) as raised:
                ImageService.upload_article_image(
                    SimpleNamespace(filename="article.jpg", read=lambda: b"image")
                )

        self.assertEqual(raised.exception.status_code, 503)
        self.assertNotIn("secret", raised.exception.message.lower())

    def test_cloudinary_upload_error_hides_provider_details(self):
        with patch("src.services.image_service._configure"):
            with patch(
                "src.services.image_service.cloudinary.uploader.upload",
                side_effect=RuntimeError("provider response includes private details"),
            ):
                with self.assertRaises(ImageUploadError) as raised:
                    ImageService.upload_article_image(
                        SimpleNamespace(filename="article.jpg", read=lambda: b"image")
                    )

        self.assertEqual(raised.exception.status_code, 502)
        self.assertNotIn("private details", raised.exception.message)

    def test_health_check_hides_database_connection_details(self):
        with self.production_config():
            app = create_app()
            with patch(
                "src.routes.health.check_db_connection",
                return_value={
                    "status": "disconnected",
                    "error": "No se pudo establecer conexión con la base de datos.",
                },
            ):
                with app.test_request_context():
                    response, status_code = health_check()

        self.assertEqual(status_code, 503)
        self.assertEqual(response.get_json()["status"], "degraded")
        self.assertEqual(
            response.get_json()["database"]["error"],
            "No se pudo establecer conexión con la base de datos.",
        )

    def test_database_health_result_does_not_expose_driver_exception(self):
        with patch(
            "src.db.get_db_cursor",
            side_effect=RuntimeError("connection password must not be exposed"),
        ):
            result = check_db_connection()

        self.assertEqual(result["status"], "disconnected")
        self.assertNotIn("password", result["error"])

    def test_cors_allows_only_configured_production_origin(self):
        with self.production_config():
            client = create_app().test_client()

        allowed = client.get(
            "/", headers={"Origin": "https://codigo-femenino.vercel.app"}
        )
        preview = client.get(
            "/", headers={"Origin": "https://preview.vercel.app"}
        )

        self.assertEqual(
            allowed.headers.get("Access-Control-Allow-Origin"),
            "https://codigo-femenino.vercel.app",
        )
        self.assertIsNone(preview.headers.get("Access-Control-Allow-Origin"))

    def admin_client_and_token(self):
        with self.production_config():
            client = create_app().test_client()
            response = client.post(
                "/api/admin/auth/login",
                json={
                    "username": self.admin_username,
                    "password": self.admin_password,
                },
            )
        self.assertEqual(response.status_code, 200, response.get_json())
        body = response.get_json()
        self.assertEqual(body["expires_in"], Config.JWT_ACCESS_TOKEN_EXPIRES)
        return client, body["access_token"]

    def test_login_rejects_invalid_credentials_without_disclosing_which_failed(self):
        with self.production_config():
            client = create_app().test_client()
            response = client.post(
                "/api/admin/auth/login",
                json={"username": self.admin_username, "password": "wrong"},
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["error"], "INVALID_CREDENTIALS")

    def test_anonymous_users_cannot_access_any_admin_operation_or_preview(self):
        with self.production_config():
            client = create_app().test_client()

        requests = (
            ("get", "/api/leads"),
            ("post", "/api/articles"),
            ("put", "/api/articles/example"),
            ("delete", "/api/articles/example"),
            ("get", "/api/articles?status=draft"),
            ("get", "/api/articles?status=archived"),
            ("get", "/api/articles?status=all"),
            ("get", "/api/articles/unpublished?preview=true"),
        )
        for method, path in requests:
            with self.subTest(method=method, path=path):
                response = getattr(client, method)(path, json={})
                self.assertEqual(response.status_code, 401, response.get_json())

    def test_missing_and_invalid_bearer_tokens_are_rejected(self):
        with self.production_config():
            client = create_app().test_client()

        response = client.get("/api/leads")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(client.head("/api/leads").status_code, 401)

        response = client.get(
            "/api/leads",
            headers={"Authorization": "Bearer not-a-jwt"},
        )
        self.assertEqual(response.status_code, 401)

    def test_expired_bearer_token_is_rejected(self):
        with self.production_config():
            app = create_app()
            client = app.test_client()
            with app.app_context():
                expired_token = create_access_token(
                    identity=self.admin_username,
                    expires_delta=timedelta(seconds=-1),
                )

        response = client.get(
            "/api/leads",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        self.assertEqual(response.status_code, 401)

    def test_missing_admin_credentials_disable_login(self):
        with self.production_config(
            APP_ENV="development",
            ADMIN_USERNAME=None,
            ADMIN_PASSWORD=None,
        ):
            client = create_app().test_client()
            response = client.post(
                "/api/admin/auth/login",
                json={"username": self.admin_username, "password": self.admin_password},
            )
            self.assertEqual(response.status_code, 503)
            self.assertEqual(
                response.get_json()["error"],
                "AUTHENTICATION_NOT_CONFIGURED",
            )

    def test_login_does_not_issue_token_for_example_configuration(self):
        with self.production_config(
            APP_ENV="development",
            ADMIN_USERNAME="admin",
            ADMIN_PASSWORD="Example-Administrator-Password",
        ):
            client = create_app().test_client()
            response = client.post(
                "/api/admin/auth/login",
                json={
                    "username": "admin",
                    "password": "Example-Administrator-Password",
                },
            )

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("access_token", response.get_json())

    def test_login_rate_limit_returns_json_429_and_is_per_client_ip(self):
        with self.production_config():
            client = create_app().test_client()
            request_data = {
                "json": {"username": "invalid", "password": "invalid"},
                "environ_overrides": {
                    "REMOTE_ADDR": "127.0.0.1",
                    "HTTP_X_FORWARDED_FOR": "198.51.100.10",
                },
            }
            for attempt in range(5):
                with self.subTest(attempt=attempt):
                    self.assertEqual(
                        client.post(
                            "/api/admin/auth/login",
                            **request_data,
                        ).status_code,
                        401,
                    )

            limited = client.post("/api/admin/auth/login", **request_data)
            self.assertEqual(limited.status_code, 429)
            self.assertEqual(limited.mimetype, "application/json")
            self.assertEqual(limited.get_json()["error"], "RATE_LIMIT_EXCEEDED")
            self.assertIn("Retry-After", limited.headers)

            another_ip = client.post(
                "/api/admin/auth/login",
                json={"username": "invalid", "password": "invalid"},
                environ_overrides={
                    "REMOTE_ADDR": "127.0.0.1",
                    "HTTP_X_FORWARDED_FOR": "198.51.100.11",
                },
            )
            self.assertEqual(another_ip.status_code, 401)

    def test_public_forms_share_rate_limit(self):
        with self.production_config():
            client = create_app().test_client()

        paths = (
            ("/api/newsletter", {"email": "reader@example.test"}),
            ("/api/guia-gratuita", {"email": "reader@example.test"}),
        )
        with patch(
            "src.routes.leads.LeadService.register_lead",
            return_value={"success": True},
        ) as register_lead:
            for attempt in range(10):
                path, payload = paths[attempt % len(paths)]
                response = client.post(
                    path,
                    json=payload,
                    environ_overrides={"REMOTE_ADDR": "198.51.100.20"},
                )
                self.assertEqual(response.status_code, 200, response.get_json())

            limited = client.post(
                "/api/leads",
                json={"email": "reader@example.test", "source": "newsletter"},
                environ_overrides={"REMOTE_ADDR": "198.51.100.20"},
            )

        self.assertEqual(limited.status_code, 429)
        self.assertEqual(limited.get_json()["error"], "RATE_LIMIT_EXCEEDED")
        self.assertEqual(register_lead.call_count, 10)

    def test_valid_token_allows_leads_and_preview_reads(self):
        client, token = self.admin_client_and_token()
        headers = {"Authorization": f"Bearer {token}"}
        lead_result = {
            "items": [],
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total_items": 0,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False,
            },
        }
        with patch("src.routes.leads.LeadService.list_leads", return_value=lead_result):
            response = client.get("/api/leads", headers=headers)
        self.assertEqual(response.status_code, 200)

        with patch(
            "src.routes.articles.ArticleService.list_articles",
            return_value={
                "items": [],
                "pagination": lead_result["pagination"],
            },
        ) as list_articles:
            response = client.get("/api/articles?status=all", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(list_articles.call_args.kwargs["status"])

        with patch(
            "src.routes.articles.ArticleService.get_article_detail",
            return_value={"slug": "draft-example", "status": "draft"},
        ):
            response = client.get(
                "/api/articles/draft-example?preview=true",
                headers=headers,
            )
        self.assertEqual(response.status_code, 200)

    def test_valid_token_allows_every_article_write_operation(self):
        client, token = self.admin_client_and_token()
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "title": "Artículo de prueba",
            "slug": "articulo-de-prueba",
            "category_id": 1,
            "excerpt": "Extracto de prueba",
        }
        with patch(
            "src.routes.articles.ArticleService.create_article",
            return_value={"slug": payload["slug"]},
        ), patch(
            "src.routes.articles.ArticleService.update_article",
            return_value={"slug": payload["slug"]},
        ), patch(
            "src.routes.articles.ArticleService.delete_article",
            return_value=True,
        ):
            self.assertEqual(
                client.post("/api/articles", json=payload, headers=headers).status_code,
                201,
            )
            self.assertEqual(
                client.put(
                    "/api/articles/articulo-de-prueba",
                    json={"title": "Título actualizado"},
                    headers=headers,
                ).status_code,
                200,
            )
            self.assertEqual(
                client.delete(
                    "/api/articles/articulo-de-prueba",
                    headers=headers,
                ).status_code,
                200,
            )
    def test_public_reads_and_signup_routes_remain_available(self):
        with self.production_config():
            client = create_app().test_client()

        category = {"id": 1, "slug": "autoestima", "name": "Autoestima"}
        with patch("src.routes.categories.CategoryService.list_categories", return_value=[category]), patch(
            "src.routes.categories.CategoryService.get_category_by_slug",
            return_value=category,
        ):
            self.assertEqual(client.get("/api/categories").status_code, 200)
            self.assertEqual(client.get("/api/categories/autoestima").status_code, 200)

        empty_page = {
            "items": [],
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total_items": 0,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False,
            },
        }
        with patch(
            "src.routes.articles.ArticleService.list_articles",
            return_value=empty_page,
        ) as list_articles:
            self.assertEqual(client.get("/api/articles").status_code, 200)
            self.assertEqual(
                list_articles.call_args.kwargs["status"],
                "published",
            )
        with patch(
            "src.routes.articles.ArticleService.get_article_detail",
            return_value={"slug": "public-article", "status": "published"},
        ) as get_article:
            self.assertEqual(
                client.get("/api/articles/public-article?preview=false").status_code,
                200,
            )
            self.assertEqual(
                get_article.call_args.kwargs["status"],
                "published",
            )

        with patch(
            "src.routes.leads.LeadService.register_lead",
            return_value={"success": True},
        ):
            for path, payload in (
                ("/api/leads", {"email": "test@example.com", "source": "newsletter"}),
                ("/api/newsletter", {"email": "test@example.com"}),
                ("/api/guia-gratuita", {"email": "test@example.com"}),
            ):
                with self.subTest(path=path):
                    response = client.post(path, json=payload)
                    self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
