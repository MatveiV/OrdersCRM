# Инструкция по подключению к серверу

## Параметры подключения
- **Домен:** orderscrm.ru
- **IP-адрес:** 185.87.48.13
- **Пользователь:** root

## Подключение через SSH
```bash
ssh root@orderscrm.ru
# или через алиас из config:
ssh orderscrm
```

## SSH-ключ
- **Файл ключа:** `C:\Users\MV\.ssh\six`
- **Публичный ключ:** `C:\Users\MV\.ssh\six.pub`

### Подключение с указанием ключа
```bash
ssh -i C:\Users\MV\.ssh\six root@185.87.48.13
```

## Настройка автоматического выбора ключа (SSH config)
В файле `C:\Users\MV\.ssh\config` настроен алиас для быстрого подключения:
```bash
ssh orderscrm
```

## Настройка SSH-ключа (выполнено)
1. SSH-ключ создан: `ssh-keygen -t ed25519 -C "orderscrm@server"`
2. Публичный ключ добавлен на сервер в `/root/.ssh/authorized_keys`
3. Парольная аутентификация отключена в `/etc/ssh/sshd_config`
4. SSH-сервис перезагружен

## Безопасность
- Приватный ключ хранится в `C:\Users\MV\.ssh\six`
- Доступ к ключу: `chmod 600 C:\Users\MV\.ssh\six`
- Парольная аутентификация отключена

## Проверка подключения
```bash
ssh -i C:\Users\MV\.ssh\six root@185.87.48.13
```