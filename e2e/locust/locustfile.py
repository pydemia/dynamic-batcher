import time
import random
import gevent
from locust import HttpUser, task, between, FastHttpUser

class QuickstartUser(FastHttpUser):
    # wait_time = between(1, 5)

    # @task
    # def hello_world(self):
    #     i = random.randint(0, 1000)
    #     self.client.post(f"/items/test/{i}", json={"content": f"{i}"})
    #     # self.client.get("/world")

    @task
    def t(self):
        def concurrent_request(x):
            i = random.randint(0, 1000)
            self.client.post(f"/items/test/{i}", json={"content": f"{i}"})

        pool = gevent.pool.Pool()
        # urls = ["/url1", "/url2", "/url3"]
        for i in range(100):
            pool.spawn(concurrent_request, i)
        pool.join()
    # @task
    # def hello_world(self):
    #     self.client.get("/hello")
    #     self.client.get("/world")

    # @task(3)
    # def view_items(self):
    #     for item_id in range(10):
    #         self.client.get(
    #             f"/item?id={item_id}",
    #             name="/item",
    #         )
    #         time.sleep(1)

    # def on_start(self):
    #     self.client.post(
    #         "/login",
    #         json={
    #             "username": "foo",
    #             "password":"bar",
    #         }
    #     )

