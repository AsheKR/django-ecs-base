# Django ECS Base

빠르게 배포하고 빠르게 시작할 수 있는 프로젝트

## 프로젝트 구조

### 1. ROOT_DIR
Production 배포와 관련된 파일을 배치해 놓는 폴더이다.
- gunicorn
- nginx
- docker
- docker-compose
- ecs-config

### 2. ROOT_DIR/sources
테스트 및 Django 실행과 관련된 파일을 배치해 놓는 폴더이다.
- pipenv
- pytest
- flake8
- pylint
- isort

### 3. ROOT_DIR/sources/app
Django APP 을 실행하는데 필요한 앱과 설정을 둔 폴더이다.

## 포함 라이브러리
- [django-secrets](https://github.com/LeeHanYeong/django-secrets-manager)
    - Django Secret 중앙관리 라이브러리
    - **Secret을 로컬에서 관리할 필요가 전혀 없다!**

## 추가 설정
- Custom User Model
- S3
- Sentry

## 프로젝트 퀄리티 관리
- pytest
- flake8
- pylint
- isort
- black

## 프로젝트에서 사용하기위해 수정해야하는 설정

### 1. AWS

#### 1-1. RDS

#### 1-2. S3

#### 1-3. Secrets Manager

아래 내용을 모두 채우고 `일반 텍스트`로 붙여넣어 사용한다.

```json
{
  "django-base": {
    "base": {},
    "dev": {
      "DJANGO_SECRET_KEY": "<CUSTOM_SECRET>"
    },
    "production": { 
      "DJANGO_SECRET_KEY": "<CUSTOM_SECRET>",
      "ALLOWED_HOSTS": [
        "*"
      ],
      "DATABASE_ENGINE": "<DATABASE_ENGINE>",
      "DATABASE_URL": "<DATABASE_URL>",
      "DATABASE_NAME": "<DATABASE_NAME>",
      "DATABASE_USER": "<DATABASE_USER>",
      "DATABASE_PASSWORD": "<DATABASE_PASSWORD>",
      "DATABASE_PORT": "<DATABASE_PORT>",
 
      "DJANGO_AWS_ACCESS_KEY_ID": "<DJANGO_AWS_ACCESS_KEY_ID>",
      "DJANGO_AWS_SECRET_ACCESS_KEY": "<DJANGO_AWS_SECRET_ACCESS_KEY>",
      "DJANGO_AWS_STORAGE_BUCKET_NAME": "<DJANGO_AWS_STORAGE_BUCKET_NAME>",

      "SENTRY_DSN": "<SENTRY_DSN>"
    }
  }
}
```

#### 1-4. IAM

**1-4-1. Secrets을 사용하기 위한 사용자**

사용자를 만들 때 `SecretsManagerReadWrite` 권한을 주고 만든다.

```ini
[<SECRET_MANAGER_NAME>]
aws_access_key_id=<SECRET_MANAGER_ACCESS_KEY>
aws_secret_access_key=<SECRET_MANAGER_SECRET_ACCESS_KEY>
```

**1-4-2. S3를 사용하기 위한 사용자**

사용자를 만들 때 `AmazonS3FullAccess` 권한을 주고 만든다.
여기서 나온 KEY들은 Secrets-Manager에 채워 넣는다.

### 2. config

#### 2-1. sources/app/config/settings/base.py

1. django-secrets-manager 를 사용하기 위해 Secret name과 `.aws/credentials` 에 등록한 profile label을 등록해주어야한다.

```python
# ENVIRON
# ------------------------------------------------------------------------------
# https://github.com/LeeHanYeong/django-aws-secrets-manager
AWS_SECRETS_MANAGER_SECRETS_NAME = "<SECRET_MANAGER_NAME>"
AWS_SECRETS_MANAGER_PROFILE = "<SECRET_MANAGER_CREDENTIALS_PROFILE>"
```

#### 2-2. sources/app/config/settings/local.py

1. django-secrets-manager에서 사용할 Environment를 설정해준다. (현재 프로젝트에서는 dev, production을 사용함)

```python
# ENVIRON
# ------------------------------------------------------------------------------
# https://github.com/LeeHanYeong/django-aws-secrets-manager
AWS_SECRETS_MANAGER_SECRETS_SECTION = "<SECRETS_DEV_SECTION>"
```

- Sample

```python
AWS_SECRETS_MANAGER_SECRETS_SECTION = "django-base:dev"
```


#### 2-2. sources/app/config/settings/production.py

1. django-secrets-manager에서 사용할 Environment를 설정해준다. (현재 프로젝트에서는 dev, production을 사용함)

```python
# ENVIRON
# ------------------------------------------------------------------------------
# https://github.com/LeeHanYeong/django-aws-secrets-manager
AWS_SECRETS_MANAGER_SECRETS_SECTION = "<SECRETS_PRODUCTION_SECTION>"
```

- Sample

```python
AWS_SECRETS_MANAGER_SECRETS_SECTION = "django-base:production"
```

### 3. TEST

#### 3-1. TOX

여기까지 왔으면 Django가 실행되는지 확인해보기위해 `sources/` 로 이동해서 코드가 잘 동작하는지 tox를 실행해본다.

#### 3-2. runserver(dev)

이번에는 `sources/app` 으로 들어와서 `./manage.py runserver`를 실행해본다.

#### 3-3. runserver(production)

이번에는 아래 명령으로 production 환경으로 바꿔준 후 `./manage.py runserver`를 실행해본다.

```shell script
export DJANGO_SETTINGS_MODULE=config.settings.production
```

### 4. Docker

Dockerfile`, `nginx/Dockerfile` 두 파일을 build 및 Push 후 아래 내용을 작성한다.

#### 4-1. Docker-compose.yml

```yaml
services:
  ...
  nginx:
    ...
    image: <niginx/Dockerfile의 본인이 사용할 DockerImage의 이름을 적는다.>
  web:
    ...
    image: <본인이 사용할 DockerImage의 이름을 적는다.>
```

#### 4-2. Docker-compose.prod.yml

```yaml
services:
  ...
  nginx:
    ...
    logging:
      ...
      options:
        awslogs-group: <web과 같은 그룹을 지정하거나 자유롭게 지정해도 좋다.>
        ...
        awslogs-stream-prefix: <본인이 nginx를 알아차릴 수 있을만한 Prefix를 지정한다.>
  web:
    ...
      logging:
      ...
      options:
          awslogs-group: <nginx와 같은 그룹을 지정하거나 자유롭게 지정해도 좋다.>
          ...
          awslogs-stream-prefix: <본인이 web임을 알아차릴 수 있을만한 Prefix를 지정한다.>
```

## Production 환경으로 도커 실행해보기

### 1. Docker 실행

nginx, gunicorn이 설정되어 있지 않고 직접 Docker에 들어가서 runserver로 확인할 수 있다.

```shell script
docker run -it -v $HOME/.aws/credentials:/root/.aws/credentials <DOCKER_FILE_NAME> /bin/bash
```

### 2. Docker-Compose 실행

실제 서비스환경과 동일하게 실행할 수 있다.

```shell script
docker-compose up
```

### 3. Docker-Compose 배포

docker-compose.prod.yml 에 aws logging 설정을 붙여서 실행해줄 수 있다.

```shell script
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 배포

### ECS CLI 다루기 위한 설정

[링크](https://github.com/AsheKR/Django-Docker-Compose-Buddy-CI-Example)

- ecsTaskExecutionRole 생성
- arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 에 Attach

```shell script
# 클러스터 생성
ecs-cli configure --cluster <Cluster 이름> --default-launch-type EC2 --region ap-northeast-2
```

### ECS IAM 사용자 추가

- IAMFullAccess
- AmazonECS_FullAccess
- AmazonSSMFullAccess

### 배포 환경 설정

#### 1. ecs-params.yml

[Parameter Store 설정방법](https://medium.com/@felipgomesilva/using-secrets-in-aws-ecs-dc43c37ce4a1)

### 배포 명령어

```shell script
# 배포!
ecs-cli compose --file docker-compose.yml --file docker-compose.prod.yml --project-name <Task 이름> up
```


# TODO

- [ ] 배포 최종 목적지에 도달했다. 블로그 포스팅하자
