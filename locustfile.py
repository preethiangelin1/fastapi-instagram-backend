from locust import HttpUser, task, between
import os
import random


class CreatePostUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.token = os.getenv("ACCESS_TOKEN")

        if not self.token:
            raise RuntimeError("ACCESS_TOKEN environment variable is required")

        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

        self.image_files = [
            "test_1mb.jpg",
            "test_5mb.jpg",
            "test_10mb.jpg",
            # "test_25mb.jpg",
        ]

    @task
    def create_post(self):
        filename = random.choice(self.image_files)
        image_path = os.path.join("~/Downloads/images", filename)

        with open(image_path, "rb") as image:
            files = {
                "image": (
                    filename,
                    image,
                    "image/jpeg",
                )
            }

            data = {
                "caption": f"Locust test post using {filename}"
            }

            with self.client.post(
                "/posts",
                headers=self.headers,
                files=files,
                data=data,
                name="POST /posts",
                catch_response=True,
            ) as response:

                if response.status_code not in (200, 201):
                    response.failure(
                        f"Status {response.status_code}: {response.text}"
                    )