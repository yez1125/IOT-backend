# IOT-backend

## Before starting, you need to download something...

- python(3.12.8)
- poetry
- mongoDB

## Poetry

### Install

#### Windows

1. Open powershell and enter the command

```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

2.Add to the PATH variable

3.Check

```bash
poetry --version
```

#### Mac

1. Open cmd and enter the command

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2.Add to the PATH variable

3.Check

```bash
poetry --version
```

learn more - [poetry](https://blog.kyomind.tw/python-poetry/)

### How to use

1. Create virtual environment

```
poetry env use python
```

2. Install dependency

```
poetry install
```

3. Start the server

a. dev mode

```
poetry run python run.py --dev
```

b. prod mode

```
poetry run python run.py --prod
```
