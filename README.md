# FastAPI with async background tasks + Prometheus + Grafana

#### This project provides a way to setup and run asynchronous (async/await) tasks using these libraries:
- [Background](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [ARQ](https://github.com/samuelcolvin/arq)
- [SAQ](https://github.com/tobymao/saq)
- [FastStream](https://github.com/airtai/faststream)
- [Celery](https://github.com/celery/celery)

#### This way can also be useful for testing your code with eager execution. You can see it in *tests/conftest.py*.

#### Finally, it shows how to monitor FastAPI app and execution of tasks with Prometheus + Grafana using these libraries:
- [Prometheus-fastapi-instrumentator (web app)](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [Prometheus-async (arq, saq, faststream)](https://github.com/hynek/prometheus-async)
- [Flower (celery)](https://github.com/mher/flower)

---

## Installation

Clone the repository:
``` bash
git clone https://github.com/ipakeev/fastapi-async-tasks
```

---

## Usage

Create .env file and adjust it:
``` bash
cp example.env .env
```


Build app image:
``` bash
docker build -t fastapi-async-tasks .
```

Run all containers:
``` bash
docker-compose up
```

---

Now you have access to these services:
- FastAPI: http://localhost:8000/docs
- Prometheus: http://localhost:9090/
- Grafana: http://localhost:3000/
- Flower: http://localhost:5555/
- SAQ Dashboard: http://localhost:8082/

Raw metrics are available here:
- FastAPI: http://localhost:8000/metrics
- ARQ: http://localhost:8001/metrics
- SAQ: http://localhost:8002/metrics
- FastStream: http://localhost:8003/metrics
- Celery: http://localhost:5555/metrics

---

## Benchmark

You can test the performance of the application and run a benchmark using [locust](https://github.com/locustio/locust):
``` bash
env endpoint={endpoint} locust --config locust/master.conf -f locust/benchmark.py -u 10 -i 1000
```

``` bash
env endpoint={endpoint} locust --config locust/master.conf -f locust/background.py -u 10 -i 1000
```

Available {endpoint}s:
- io/simple
- io/thread
- cpu/simple
- cpu/process

---