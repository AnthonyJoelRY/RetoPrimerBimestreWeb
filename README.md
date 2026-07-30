# Reto Primer Bimestre — Desarrollo Web

Análisis y documentación del diseño de una plataforma web B2B mayorista-minorista con enfoque en inclusión digital.

## Desarrollado por:
- Leandro Saquisari
- Anthony Romero 

## Descripción

MayorApp conecta empresas mayoristas con tiendas minoristas, automatizando pedidos, pagos y entregas. Incluye interfaz visual iconográfica, entrada de voz y geolocalización para usuarios con bajo nivel de alfabetización.

## Actores del Sistema

| Actor | Rol |
|-------|-----|
| Mayorista | Registra productos, gestiona pedidos y controla inventario |
| Vendedor | Ejecuta ventas presenciales y rinde cuentas al mayorista |
| Tienda Minorista | Realiza pedidos mediante interfaz visual simplificada |
| Administrador | Gestiona mayoristas y el modelo de monetización |

## Estructura del Repositorio

```
PRESENTACION-1BIM/
├── analisis_reto/
│   ├── Analisis_reto.docx
│   └── Analisis_reto.pdf
└── analisis_reto_latex/
    ├── analisis_reto.tex
    ├── analisis_reto.pdf
    └── images/
```

## Sprints

| Sprint | Funcionalidad |
|--------|--------------|
| Sprint 1 | Autenticación JWT por rol, registro de mayoristas |
| Sprint 2 | Catálogo de productos, sincronización de stock |
| Sprint 3 | Marketplace visual, geolocalización, nota de voz |
| Sprint 4 | Flujo completo de pedidos y estados |
| Sprint 5 | Módulo de pagos (efectivo y digital) |
| Sprint 6 | Panel de administrador, pruebas de integración |

## App Web

- App: https://anthonyjoel.pythonanywhere.com
- Credenciales: https://utpl-my.sharepoint.com/:t:/g/personal/lisaquisari_utpl_edu_ec/IQBwnWAGanohRYXDn8qrnF2oAQG9RKYzRfk33edtYkegYUQ?e=OfuTsF

## Compilar LaTeX

```bash
cd analisis_reto_latex
pdflatex analisis_reto.tex
pdflatex analisis_reto.tex
```

## Instalación y ejecución del proyecto

### 1. Requisitos previos

- Python 3.10 o superior
- pip

### 2. Crear y activar entorno virtual

```bash
cd ProyectoBimestralDjango
python3 -m venv entorno
source entorno/bin/activate   # En Windows: entorno\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
cd miProyectoDjango
python manage.py migrate
```

### 5. Iniciar la aplicación

```bash
python manage.py runserver
```

La aplicación quedará disponible en `http://127.0.0.1:8000/`.

### 6. Crear un superusuario

Para acceder al panel de administración de Django (`/admin`), es necesario crear un superusuario:

```bash
python manage.py createsuperuser
```

Se te pedirá:
- **Username**: nombre de usuario para iniciar sesión
- **Email**: correo electrónico (opcional, se puede dejar vacío)
- **Password**: contraseña (no se muestra en pantalla mientras se escribe)

Una vez creado, inicia sesión en `http://127.0.0.1:8000/admin` con las credenciales ingresadas.
