# Инструкция по подключению к серверу

## Параметры подключения
- **Домен:** orderscrm.ru (DNS не настроен — используйте IP)
- **IP-адрес:** 185.87.48.13
- **Пользователь:** root
- **SSH-ключ:** `C:\Users\MV\.ssh\six`

## Подключение через SSH

```bash
ssh -i C:\Users\MV\.ssh\six root@185.87.48.13
```

## SSH config

В `C:\Users\MV\.ssh\config` настроен алиас:

```bash
ssh orderscrm
```

## Команды на сервере

```bash
# Статус контейнеров
docker ps

# Логи бэкенда
docker logs -f orderscrm_backend

# Пересборка после изменений
docker compose build --no-cache backend && docker compose up -d

# Деплой фронтенда
docker cp /tmp/. orderscrm_nginx:/usr/share/nginx/html/
docker cp /tmp/admin/. orderscrm_nginx:/usr/share/nginx/html/admin/
docker restart orderscrm_nginx

# Бэкап БД
docker exec orderscrm_postgres pg_dump -U crm_user crm_db > backup.sql
```

## Безопасность

- Приватный ключ: `C:\Users\MV\.ssh\six` (chmod 600)
- Парольная аутентификация отключена в `/etc/ssh/sshd_config`
- Публичный ключ в `/root/.ssh/authorized_keys`
