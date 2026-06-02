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

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | React.js + Tailwind CSS |
| Backend | Django + Django REST Framework |
| Autenticación | JWT (SimpleJWT) |
| Base de Datos | SQLite |
| Servidor Web | Nginx + Gunicorn |

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

## Prototipo

- App: https://wholesale-platform--romerojoelya.replit.app
- Credenciales: https://drive.google.com/file/d/1FI_932e9UU-dHqA4TcE2mHI8A8WDARh0/view?usp=sharing

## Compilar LaTeX

```bash
cd analisis_reto_latex
pdflatex analisis_reto.tex
pdflatex analisis_reto.tex
```
