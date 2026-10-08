# Sistema Biblioteca

Aplicacion Django para administrar socios, libros y prestamos, con interfaz web y API RESTful protegida con JWT.

## API REST

| Recurso | Listar/crear | Consultar/actualizar/eliminar |
| --- | --- | --- |
| Socios | `GET/POST /api/socios/` | `GET/PUT/DELETE /api/socios/<id>/` |
| Libros | `GET/POST /api/libros/` | `GET/PUT/DELETE /api/libros/<id>/` |
| Prestamos | `GET/POST /api/prestamos/` | `GET/PUT/DELETE /api/prestamos/<id>/` |

Los endpoints requieren autenticacion. Los administradores pueden administrar socios y libros; los usuarios autenticados pueden consultar recursos y registrar o actualizar prestamos. Los campos privados de socios no se exponen a usuarios no administrativos.

### JWT y documentacion

- Obtener tokens: `POST /api/token/` con `username` y `password`.
- Renovar el access token: `POST /api/token/refresh/` con `refresh`.
- Swagger UI: `/api/swagger/`.
- ReDoc: `/api/redoc/`.
- Esquema OpenAPI: `/api/schema/`.

En Swagger selecciona **Authorize** y envia `Bearer <access_token>` para probar los endpoints protegidos.

## Instalacion local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DB_ENGINE = "sqlite"
python manage.py migrate
python manage.py runserver
```

Para usar MySQL/MariaDB, omite `DB_ENGINE=sqlite` y define `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`.

## Despliegue en AWS EC2 con LAMP, Gunicorn y Nginx

MySQL/MariaDB del stack LAMP funciona como base de datos; Gunicorn ejecuta Django mediante WSGI y Nginx recibe las solicitudes publicas, sirve archivos estaticos/media y las reenvia a Gunicorn. No uses `runserver` como proceso de produccion.

### Preparacion del proyecto y MySQL

```bash
cd /ruta/al/proyecto
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY='genera-una-clave-larga-y-privada'
export DEBUG=False
export ALLOWED_HOSTS='IP_PUBLICA,DNS_PUBLICO'
export CSRF_TRUSTED_ORIGINS='http://IP_PUBLICA,http://DNS_PUBLICO'
export DB_ENGINE=mysql
export DB_NAME='biblioteca_db'
export DB_USER='usuario_mysql'
export DB_PASSWORD='********'
export DB_HOST='localhost'
export DB_PORT='3306'

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

Comprueba la conexion con `mysql -u usuario_mysql -p biblioteca_db` y confirma que MySQL/MariaDB esta activo con `sudo systemctl status mysql` o `sudo systemctl status mariadb`.

### Probar Gunicorn directamente

```bash
source .venv/bin/activate
gunicorn --bind 127.0.0.1:8000 --workers 3 sistema_biblioteca.wsgi:application
```

En otra sesion SSH verifica:

```bash
curl -I http://127.0.0.1:8000/
curl -I http://127.0.0.1:8000/api/swagger/
```

### Servicio systemd para Gunicorn

Guarda `/etc/systemd/system/biblioteca.service`, ajustando usuario y rutas:

```ini
[Unit]
Description=Gunicorn Sistema Biblioteca
After=network.target mysql.service

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Sistema-Biblioteca
EnvironmentFile=/home/ubuntu/Sistema-Biblioteca/.env
ExecStart=/home/ubuntu/Sistema-Biblioteca/.venv/bin/gunicorn --workers 3 --bind unix:/run/biblioteca.sock sistema_biblioteca.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now biblioteca
sudo systemctl status biblioteca
sudo journalctl -u biblioteca -n 50 --no-pager
```

### Configuracion Nginx

Guarda `/etc/nginx/sites-available/biblioteca` y reemplaza `server_name`:

```nginx
server {
    listen 80;
    server_name IP_PUBLICA DNS_PUBLICO;
    client_max_body_size 10M;

    location /static/ {
        alias /home/ubuntu/Sistema-Biblioteca/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/Sistema-Biblioteca/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/biblioteca.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/biblioteca /etc/nginx/sites-enabled/biblioteca
sudo nginx -t
sudo systemctl reload nginx
```

Pruebas desde otra maquina:

```bash
curl -I http://IP_PUBLICA/
curl -I http://IP_PUBLICA/api/swagger/
curl -I http://IP_PUBLICA/api/token/
```

Para la evaluacion se debe evidenciar: instancia EC2 activa, conexion SSH, entorno virtual, servicio MySQL/MariaDB, servicio `biblioteca`/Gunicorn activo, Nginx activo, migraciones, aplicacion web, `/api/swagger/`, `/api/token/` y una prueba de endpoint autenticado desde la IP o DNS publico.

## Pruebas automatizadas

```powershell
$env:DB_ENGINE = "sqlite"
python manage.py check
python manage.py test
python manage.py spectacular --file openapi.yml --validate
```
