# PROMPT PARA REPLIT — PROTOTIPO PLATAFORMA B2B MAYORISTA-MINORISTA

\---

## CONTEXTO DEL PROYECTO

Construye un prototipo funcional de una plataforma web B2B tipo marketplace que conecta **empresas mayoristas** con **tiendas minoristas**. La tienda se registra libremente y puede ver y comprarle a cualquier mayorista activo (como Rappi pero entre negocios). Cada mayorista gestiona su catálogo, inventario y vendedores. El sistema soporta dos flujos de pago y descuenta inventario automáticamente por cada venta confirmada.

El proceso de pedidos ocurre de dos formas:

* **Modo autoservicio:** la tienda minorista entra a la app y hace el pedido sola
* **Modo asistido:** el vendedor visita la tienda en persona y crea el pedido desde su panel en nombre de esa tienda

\---

## STACK TECNOLÓGICO

* **Frontend:** React + TypeScript + Tailwind CSS + Wouter (router)
* **Backend:** Node.js + Express + TypeScript
* **Base de datos:** PostgreSQL con Drizzle ORM
* **Mapas:** Leaflet.js (open source, sin API key)
* **Voz:** Web Speech API nativa del navegador
* **Pagos simulados:** Formulario propio (sin pasarela real en el prototipo)
* **Autenticación:** JWT almacenado en localStorage, expiración 8h
* **Imágenes:** Almacenamiento local en `/uploads` con Multer
* **HTTP Client:** @workspace/api-client-react (generado con orval)

\---

## ESTRUCTURA DE ROLES Y RUTAS

El sistema tiene **4 roles** con interfaces completamente separadas:

* **ROL 1 — ADMINISTRADOR** (`/admin`): gestiona mayoristas, suscripciones y comisiones globales
* **ROL 2 — EMPRESA MAYORISTA** (`/mayorista`): catálogo, vendedores, pedidos e inventario
* **ROL 3 — VENDEDOR** (`/vendedor`): toma pedidos en nombre de tiendas, gestiona cobros en efectivo
* **ROL 4 — TIENDA MINORISTA** (`/tienda`): marketplace visual, ve todos los mayoristas activos y hace pedidos

\---

## ESTRUCTURA DE ARCHIVOS DEL PROYECTO

```
artifacts/
  api-server/
    src/
      routes/         → auth.ts, mayoristas.ts, productos.ts, pedidos.ts,
                        pagos.ts, tiendas.ts, vendedores.ts, rendiciones.ts, admin.ts
      middlewares/
        auth.ts       → requireAuth, requireRole, signToken
      lib/
        logger.ts
    uploads/
      imagenes/
      audio/
  b2b-marketplace/
    src/
      pages/
        auth/         → login-mayorista, login-tienda, login-vendedor,
                        login-admin, registro-mayorista, registro-tienda
        admin/        → dashboard, mayoristas, configuracion, suscripciones
        mayorista/    → dashboard, productos, inventario, pedidos,
                        vendedores, rendiciones, reportes, mi-cuenta
        tienda/
          index.tsx         → lista de mayoristas (pantalla principal)
          layout.tsx
          mayorista-catalog.tsx  → catálogo de un mayorista con modal de cantidad
          carrito.tsx
          entrega.tsx
          confirmacion.tsx
          mis-pedidos.tsx
        vendedor/     → dashboard, nuevo-pedido, cobros, rendicion, cambiar-password
      components/
        layout/
          protected-route.tsx
        ui/           → shadcn components
      lib/
        auth.tsx      → AuthProvider, useAuth
        cart.tsx      → CartProvider, useCart
      App.tsx
      main.tsx
```

\---

## BASE DE DATOS — ESQUEMA COMPLETO (PostgreSQL)

```sql
-- Mayoristas
CREATE TABLE mayoristas (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  categoria TEXT,                        -- Bebidas | Abarrotes | Lácteos | Limpieza | Otro
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,                -- bcrypt hash
  telefono TEXT,
  logo\\\_url TEXT,
  estado TEXT DEFAULT 'pendiente\\\_pago',  -- pendiente\\\_pago | activo | suspendido
  plan TEXT DEFAULT 'suscripcion',       -- suscripcion | comision | mixto
  tarifa\\\_anual REAL DEFAULT 0,
  porcentaje\\\_comision REAL DEFAULT 0,
  fecha\\\_vencimiento TEXT,
  created\\\_at TIMESTAMP DEFAULT NOW()
);

-- Vendedores (solo el mayorista los crea)
CREATE TABLE vendedores (
  id SERIAL PRIMARY KEY,
  mayorista\\\_id INTEGER REFERENCES mayoristas(id),
  nombre TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,                -- bcrypt hash
  primer\\\_login INTEGER DEFAULT 1,        -- 1 = forzar cambio de contraseña
  tipo\\\_perfil TEXT DEFAULT 'general',    -- general | especializado
  producto\\\_asignado\\\_id INTEGER,
  activo INTEGER DEFAULT 1
);

-- Productos
CREATE TABLE productos (
  id SERIAL PRIMARY KEY,
  mayorista\\\_id INTEGER REFERENCES mayoristas(id),
  nombre TEXT NOT NULL,
  descripcion TEXT,
  foto\\\_url TEXT NOT NULL,                -- OBLIGATORIO, usada en interfaz visual
  precio REAL NOT NULL,
  stock INTEGER NOT NULL DEFAULT 0,
  minimo\\\_compra INTEGER DEFAULT 1,
  unidad TEXT DEFAULT 'unidad',          -- unidad | caja | kg
  activo INTEGER DEFAULT 1
);

-- Tiendas minoristas (no pertenecen a ningún mayorista)
CREATE TABLE tiendas (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  telefono TEXT UNIQUE NOT NULL,         -- login por teléfono
  password TEXT NOT NULL,                -- bcrypt hash del PIN de 4 dígitos
  lat REAL,
  lng REAL,
  direccion\\\_texto TEXT
);

-- Admins
CREATE TABLE admins (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL                 -- bcrypt hash
);

-- Pedidos
CREATE TABLE pedidos (
  id SERIAL PRIMARY KEY,
  tienda\\\_id INTEGER REFERENCES tiendas(id),
  mayorista\\\_id INTEGER REFERENCES mayoristas(id),
  vendedor\\\_id INTEGER REFERENCES vendedores(id),
  creado\\\_por TEXT DEFAULT 'tienda',      -- tienda | vendedor
  estado TEXT DEFAULT 'pendiente',       -- pendiente | validado | en\\\_camino | entregado | cancelado
  tipo\\\_pago TEXT NOT NULL,               -- efectivo | digital
  total REAL NOT NULL,
  comision\\\_plataforma REAL DEFAULT 0,
  cobro\\\_confirmado INTEGER DEFAULT 0,
  nota\\\_voz\\\_url TEXT,
  lat\\\_entrega REAL,
  lng\\\_entrega REAL,
  direccion\\\_entrega TEXT,
  telefono\\\_contacto TEXT,
  created\\\_at TIMESTAMP DEFAULT NOW()
);

-- Detalle de pedido
CREATE TABLE pedido\\\_items (
  id SERIAL PRIMARY KEY,
  pedido\\\_id INTEGER REFERENCES pedidos(id),
  producto\\\_id INTEGER REFERENCES productos(id),
  cantidad INTEGER NOT NULL,
  precio\\\_unitario REAL NOT NULL,
  subtotal REAL NOT NULL
);

-- Pagos
CREATE TABLE pagos (
  id SERIAL PRIMARY KEY,
  pedido\\\_id INTEGER REFERENCES pedidos(id),
  metodo TEXT NOT NULL,                  -- efectivo | tarjeta | transferencia
  monto REAL NOT NULL,
  estado TEXT DEFAULT 'pendiente',       -- pendiente | confirmado | rechazado
  referencia TEXT,
  created\\\_at TIMESTAMP DEFAULT NOW()
);

-- Rendiciones del vendedor
CREATE TABLE rendiciones (
  id SERIAL PRIMARY KEY,
  vendedor\\\_id INTEGER REFERENCES vendedores(id),
  mayorista\\\_id INTEGER REFERENCES mayoristas(id),
  total\\\_cobrado REAL NOT NULL,
  total\\\_comision REAL DEFAULT 0,
  estado TEXT DEFAULT 'pendiente',       -- pendiente | confirmado
  fecha TIMESTAMP DEFAULT NOW(),
  observacion TEXT
);

-- Configuración global de la plataforma
CREATE TABLE configuracion (
  id SERIAL PRIMARY KEY,
  porcentaje\\\_comision\\\_default REAL DEFAULT 3,
  tarifa\\\_suscripcion\\\_anual REAL DEFAULT 299,
  tarifa\\\_mixto\\\_anual REAL DEFAULT 149,
  porcentaje\\\_mixto REAL DEFAULT 1.5
);

-- Movimientos de stock
CREATE TABLE movimientos\\\_stock (
  id SERIAL PRIMARY KEY,
  producto\\\_id INTEGER REFERENCES productos(id),
  pedido\\\_id INTEGER REFERENCES pedidos(id),
  cantidad INTEGER NOT NULL,
  tipo TEXT NOT NULL,                    -- venta | ajuste\\\_manual
  fecha TIMESTAMP DEFAULT NOW()
);
```

\---

## AUTENTICACIÓN — MIDDLEWARE Y JWT

```typescript
// middlewares/auth.ts
const JWT\\\_SECRET = process.env.JWT\\\_SECRET || "mayorapp\\\_secret\\\_2024";

export function requireAuth(req, res, next) {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) return res.status(401).json({ error: "No token provided" });
  const token = header.slice(7);
  try {
    const payload = jwt.verify(token, JWT\\\_SECRET);
    req.user = payload;
    next();
  } catch {
    res.status(401).json({ error: "Invalid token" });
  }
}

export function signToken(payload) {
  return jwt.sign(payload, JWT\\\_SECRET, { expiresIn: "8h" });
}
```

El frontend guarda el token así tras el login:

```typescript
const { login } = useAuth();
const data = await response.json();
login(data.token);  // guarda en localStorage y actualiza el estado
```

Cada request incluye el token automáticamente:

```typescript
headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
```

El `ProtectedRoute` verifica rol así:

```typescript
if (!isAuthenticated) setLocation("/");
else if (!allowedRoles.includes(user.rol)) setLocation(`/${user.rol}/dashboard`);
```

**IMPORTANTE:** El servidor Express debe incluir al final, después de todas las rutas API, el catch-all para servir el frontend:

```typescript
app.use(express.static(path.join(\\\_\\\_dirname, '../b2b-marketplace/dist')));
app.get('\\\*', (req, res) => {
  res.sendFile(path.join(\\\_\\\_dirname, '../b2b-marketplace/dist/index.html'));
});
```

\---

## MÓDULOS Y FUNCIONALIDADES DETALLADAS

### MÓDULO 1 — LANDING Y AUTENTICACIÓN

**Landing page** (`/`)

* Fondo con degradado verde oscuro (`#052e16` → `#15803D`)
* Logo de la plataforma centrado
* Tres botones grandes apilados:

  * 🏭 "Soy Mayorista" → `/login/mayorista`
  * 🏪 "Tengo una Tienda" → `/login/tienda`
  * 👤 "Soy Vendedor" → `/login/vendedor`
* Texto pequeño: "¿Administrador?" → `/login/admin`

**Logins**

* `/login/mayorista` → email + contraseña | link → `/registro/mayorista`
* `/login/tienda` → teléfono + PIN de 4 inputs individuales (foco automático al siguiente) | link → `/registro/tienda`
* `/login/vendedor` → email + contraseña (sin auto-registro)
* Todos los logins tienen botón de mostrar/ocultar contraseña
* Todos los paneles tienen botón de **cerrar sesión** visible en el header que ejecuta:

```typescript
localStorage.removeItem("token");
window.location.href = "/";
```

\---

### MÓDULO 2 — REGISTRO DE MAYORISTA (`/registro/mayorista`)

**Paso 1 — Datos de la empresa**

* Nombre comercial, categoría (selector), email, teléfono
* Contraseña + confirmación (mínimo 8 caracteres, toggle mostrar/ocultar)
* Logo (subida con preview, opcional)

**Paso 2 — Plan de suscripción**

* 3 radio cards seleccionables con borde verde al elegir:

  * 💳 Suscripción anual fija
  * 📊 Solo comisión por venta
  * 🔀 Plan mixto

```
POST /api/auth/registro-mayorista
1. Verificar email único
2. bcrypt.hash(password, 10)
3. INSERT mayoristas con estado = 'pendiente\\\_pago'
4. Responder con JWT
5. Redirigir a /mayorista/dashboard (muestra banner de cuenta en revisión)
```

\---

### MÓDULO 3 — REGISTRO DE TIENDA (`/registro/tienda`)

**Pantalla única — 4 campos:**

* 📱 Teléfono (`inputmode="tel"`)
* 🏪 Nombre de la tienda
* 🔑 PIN de 4 dígitos — 4 inputs individuales, foco automático
* 🔑 Confirmar PIN

```
POST /api/auth/registro-tienda
1. Verificar teléfono único
2. bcrypt.hash(pin, 10)
3. INSERT tiendas (sin mayorista\\\_id — marketplace libre)
4. Responder con JWT → redirigir a /tienda
```

\---

### MÓDULO 4 — CREACIÓN DE VENDEDORES (solo desde panel mayorista)

* El mayorista los crea desde `/mayorista/vendedores`
* Tipo: general (todo el catálogo) o especializado (un producto asignado)
* Al crear: contraseña temporal mostrada **una sola vez**
* `primer\\\_login = 1` → redirige forzosamente a `/vendedor/cambiar-password`

\---

### MÓDULO 5 — PANEL MAYORISTA

**5.1 Dashboard** — métricas del día, pedidos pendientes, stock crítico, rendiciones pendientes

**5.2 Catálogo** (`/mayorista/productos`)

* CRUD completo con foto obligatoria, precio, stock, mínimo de compra
* Toggle activo/inactivo

**5.3 Inventario** (`/mayorista/inventario`)

* Alertas de stock: 🟢 >20 | 🟡 5-20 | 🔴 ≤4 | ⚫ 0 (oculto al minorista)
* Ajuste manual de stock
* Log de movimientos por pedido

**5.4 Pedidos** (`/mayorista/pedidos`)

* Filtros por estado y fecha
* Cada tarjeta muestra: tienda, teléfono de contacto, productos, total, tipo de pago, "Creado por: Tienda/Vendedor"
* Mapa Leaflet con pin de entrega
* Botón ▶ para reproducir nota de voz
* Flujo: Validar → En camino → Entregado | Cancelar
* **Al Validar:** transacción atómica que descuenta stock

**5.5 Vendedores** (`/mayorista/vendedores`)

* Crear, activar/desactivar, ver ventas por vendedor

**5.6 Rendiciones** (`/mayorista/rendiciones`)

* Lista de rendiciones de vendedores
* Botón "Confirmar rendición"

**5.7 Reportes** — gráficos con Recharts, producto más vendido, comisiones

**5.8 Mi Cuenta** — datos, plan, cambio de contraseña

\---

### MÓDULO 6 — INTERFAZ MINORISTA — MARKETPLACE VISUAL

> REGLA DE ORO: usable sin leer una sola palabra.

**Rutas:**

```
/tienda                      → lista de mayoristas (pantalla principal)
/tienda/mayorista/:id        → catálogo del mayorista (componente separado, NO dentro del layout)
/tienda/carrito
/tienda/entrega
/tienda/confirmacion
/tienda/mis-pedidos
```

**CRÍTICO — App.tsx debe tener esta ruta ANTES de `/tienda/:rest\\\*`:**

```tsx
<Route path="/tienda/mayorista/:id">
  <ProtectedRoute allowedRoles={\\\["tienda"]}>
    <MayoristaCatalog />
  </ProtectedRoute>
</Route>
<Route path="/tienda/:rest\\\*">
  <ProtectedRoute allowedRoles={\\\["tienda"]}>
    <TiendaLayout />
  </ProtectedRoute>
</Route>
```

**6.1 Lista de mayoristas** — grilla 2 columnas, logo, nombre, categoría con badge de color. Solo `estado = 'activo'`.

**6.2 Catálogo del mayorista** (`mayorista-catalog.tsx`)

* Header con botón ← volver y nombre del mayorista
* Grilla 2 columnas móvil / 3 desktop
* Cada tarjeta: foto `aspect-ratio:1/1`, nombre, precio, badge de mínimo, botón **"+ Agregar"** visible en la parte inferior
* Stock = 0: overlay con candado, sin botón agregar
* Al tocar "+ Agregar": abre modal con:

  * Imagen reducida (`h-48`, no `aspect-square`) para que los botones sean visibles
  * Nombre y precio
  * Selector +/- respetando mínimo de compra
  * Botón "Agregar al Carrito • $XX.XX"
  * `DialogContent` con `overflow-y-auto max-h-\\\[90vh]` para ser scrolleable
* Alerta si intenta mezclar mayoristas en el carrito
* Barra flotante inferior cuando hay items: "Pagar $XX.XX" → `/tienda/carrito`

**6.3 Carrito** — lista de items, totales, botón "PEDIR 🚛"

**6.4 Entrega** — 3 pasos máximo:

1. Mapa Leaflet con pin arrastrable
2. Campo de dirección + botón de micrófono (Web Speech API, graba y transcribe)
3. Selector de pago: 💵 Efectivo | 💳 Digital (formulario simulado)

**6.5 Confirmación** — checkmark animado SVG, número de pedido, fotos en fila

**6.6 Mis pedidos** — agrupados por mayorista, estados con íconos

\---

### MÓDULO 7 — PANEL DE VENDEDOR

**7.1** Primer login → forzar `/vendedor/cambiar-password` antes de cualquier otra pantalla

**7.2 Dashboard** — pedidos pendientes de cobro, total del mes

**7.3 Toma de pedidos** (`/vendedor/nuevo-pedido`)

* Buscar tienda por nombre o teléfono
* Seleccionar productos (respeta perfil: general o especializado)
* Confirmar con tipo de pago

**7.4 Cobros** (`/vendedor/cobros`)

* Pedidos en efectivo pendientes
* Botón "Marcar como cobrado"
* Botón "Enviar rendición"

**7.5 Rendición** (`/vendedor/rendicion`)

* Resumen de cobros, comisión descontada, monto a entregar
* INSERT en tabla rendiciones

\---

### MÓDULO 8 — PANEL ADMIN

* Activar / Suspender / Reactivar mayoristas
* Configuración global de tarifas y comisiones
* Dashboard de métricas generales

\---

## FLUJOS CRÍTICOS

### Validación y descuento de stock (transacción atómica)

```
POST /api/pedidos/:id/validar
  1. Verificar estado === 'pendiente'
  2. BEGIN TRANSACTION
  3. Por cada item:
     a. SELECT stock — si insuficiente → ROLLBACK, 409
     b. UPDATE stock = stock - cantidad
  4. UPDATE pedido estado = 'validado'
  5. Si plan incluye comisión → calcular y guardar
  6. INSERT movimientos\\\_stock
  7. COMMIT → 200
```

### Verificación de stock al agregar al carrito

```
GET /api/productos/:id  →  devuelve stock actual
Frontend: si stock < minimo\\\_compra → deshabilitar botón
          si stock < cantidad elegida → "Solo quedan X disponibles"
```

### Nota de voz

```
1. navigator.mediaDevices.getUserMedia({ audio: true })
2. MediaRecorder graba mientras botón presionado (fondo rojo pulsante)
3. Al soltar: blob → POST /api/pedidos/upload-audio (Multer)
4. SpeechRecognition transcribe en tiempo real al campo de texto
5. pedido.nota\\\_voz\\\_url = ruta del archivo
```

### Pago digital simulado (Opción B)

```
POST /api/pagos/procesar
  1. Validar monto === pedido.total
  2. Delay 2s simulado
  3. INSERT pagos estado = 'confirmado'
  4. Disparar validación + descuento de stock
  5. 200
```

### Flujo completo Opción A (efectivo)

```
1. Vendedor crea pedido → tipo\\\_pago = 'efectivo'
2. Mayorista valida (descuenta stock) → marca en camino
3. Vendedor entrega y cobra → marca cobrado
4. Vendedor agrupa cobros → envía rendición
5. Mayorista confirma rendición → marca entregado
```

\---

## API REST — ENDPOINTS

```
AUTH
POST  /api/auth/login-mayorista
POST  /api/auth/login-tienda          -- Body: { telefono, pin }
POST  /api/auth/login-vendedor
POST  /api/auth/login-admin
GET   /api/auth/me                    -- verifica token, devuelve user
POST  /api/auth/registro-mayorista
POST  /api/auth/registro-tienda       -- Body: { telefono, nombre, pin }
PUT   /api/auth/cambiar-password

MAYORISTAS
GET   /api/mayoristas                 -- todos los activos (para marketplace)
GET   /api/mayoristas/:id
PUT   /api/mayoristas/:id
PUT   /api/mayoristas/:id/activar
PUT   /api/mayoristas/:id/suspender
PUT   /api/mayoristas/:id/reactivar

PRODUCTOS
GET   /api/productos?mayorista\\\_id=X   -- activos con stock > 0
GET   /api/productos/:id              -- stock en tiempo real
POST  /api/productos
PUT   /api/productos/:id
DELETE /api/productos/:id
PUT   /api/productos/:id/stock

PEDIDOS
GET   /api/pedidos?mayorista\\\_id=X\\\&estado=Y
GET   /api/pedidos?tienda\\\_id=X
GET   /api/pedidos?vendedor\\\_id=X
POST  /api/pedidos
PUT   /api/pedidos/:id/validar
PUT   /api/pedidos/:id/estado
POST  /api/pedidos/upload-audio

PAGOS
POST  /api/pagos/procesar

VENDEDORES
GET   /api/vendedores?mayorista\\\_id=X
POST  /api/vendedores
PUT   /api/vendedores/:id

RENDICIONES
GET   /api/rendiciones?mayorista\\\_id=X
GET   /api/rendiciones?vendedor\\\_id=X
POST  /api/rendiciones
PUT   /api/rendiciones/:id/confirmar

TIENDAS
GET   /api/tiendas?q=X               -- búsqueda por nombre o teléfono
GET   /api/tiendas/:id/pedidos

ADMIN
GET   /api/admin/stats
GET   /api/admin/configuracion
PUT   /api/admin/configuracion
```

\---

## DATOS SEMILLA (SEED)

```
Admin:      admin@plataforma.com / admin123

Mayorista 1: "Distribuidora López"
  email:     lopez@demo.com / demo123
  categoria: Abarrotes — plan mixto — comisión 3% — estado: ACTIVO
  Productos (fotos de Unsplash ?w=400):
    - Arroz Súper Extra 25kg       stock:150  mín:5   foto: photo-1586201375761-83865001e31c
    - Aceite La Favorita 1L        stock:80   mín:3   foto: photo-1474979266404-7eaacbcd87c5
    - Harina 1kg                   stock:60   mín:4   foto: photo-1509440159596-0249088772ff
    - Azúcar 1kg                   stock:4    mín:2   foto: photo-1548873752-0c1f33c15c4a  ← alerta roja
    - Sal 500g                     stock:0            foto: photo-1518110925495-5fe2fda0442c ← agotado

Mayorista 2: "Bebidas Andinas"
  email:     andinas@demo.com / demo123
  categoria: Bebidas — plan suscripción — estado: ACTIVO
  Productos:
    - Agua mineral 500ml           stock:200  mín:12  foto: photo-1548839140-29a749e1cf4d
    - Gaseosa 2L                   stock:90   mín:6   foto: photo-1621506289937-a8e4df240d0b
    - Jugo de naranja 1L           stock:5    mín:3   foto: photo-1600271886742-f049cd451bba ← alerta roja

Tiendas:
  - "Tienda Doña Rosa"      teléfono: 0991111111  PIN: 1234
  - "Minimarket El Centro"  teléfono: 0992222222  PIN: 1234

Vendedores de López:
  - carlos@lopez.com / vendedor123   perfil: general     primer\\\_login: 0
  - ana@lopez.com / vendedor123      perfil: especializado → Arroz  primer\\\_login: 0

Vendedores de Andinas:
  - pedro@andinas.com / vendedor123  perfil: general     primer\\\_login: 0
  - maria@andinas.com / vendedor123  perfil: especializado → Agua  primer\\\_login: 0

Pedidos demo (4):
  - Tienda Doña Rosa → López       estado: pendiente   pago: digital
  - Tienda Doña Rosa → Andinas     estado: en\\\_camino   pago: efectivo  creado\\\_por: vendedor
  - Minimarket → López             estado: entregado   pago: digital
  - Minimarket → Andinas           estado: validado    pago: efectivo

IMPORTANTE: Todas las contraseñas deben guardarse con bcrypt.hash(password, 10)
Los mayoristas del seed deben tener estado = 'activo' (no 'pendiente\\\_pago')
```

\---

## DISEÑO UI — GUÍA VISUAL

**Paleta de colores:**

* Primario: `#16A34A` (verde)
* Primario oscuro: `#15803D`
* Fondo oscuro landing: `#052e16`
* Acento: `#F59E0B` (ámbar)
* Peligro: `#DC2626` (rojo)
* Fondo app: `#F0FDF4`
* Texto: `#052e16`

**Tipografía:**

* Paneles mayorista/admin/vendedor: Inter, 14px base
* Interfaz minorista: Inter, **18px mínimo**, bold en precios

**Componentes clave interfaz minorista:**

* Botones mínimo 56px de altura
* Fotos con `aspect-ratio: 1/1` y `object-fit: cover`
* Modal de producto: imagen `h-48` (no aspect-square) para que quepan los botones
* `DialogContent` con `overflow-y-auto max-h-\\\[90vh]`
* Skeleton loaders en catálogo y lista de mayoristas
* Checkmark animado en confirmación: SVG con `stroke-dashoffset`
* Botón micrófono: fondo rojo pulsante mientras graba

**Botón cerrar sesión:** presente en el header de TODOS los paneles (mayorista, tienda, vendedor, admin), color rojo, alineado a la derecha. Ejecuta `localStorage.removeItem("token"); window.location.href = "/";`

\---

## INSTRUCCIONES CRÍTICAS PARA REPLIT

1. Usar `concurrently` para correr frontend (puerto 5173) y backend (puerto 3001) con un solo `npm run dev`
2. Proxy en Vite: `/api/\\\*` → `localhost:3001`
3. Variables de entorno: `JWT\\\_SECRET`, `DATABASE\\\_URL`, `PORT=3001`
4. **El servidor Express DEBE incluir el catch-all al final** para servir el frontend en rutas como `/mayorista/dashboard` (de lo contrario da 404)
5. La ruta `/tienda/mayorista/:id` debe ir ANTES de `/tienda/:rest\\\*` en el router de React
6. Imágenes del seed: URLs de Unsplash formato `https://images.unsplash.com/photo-XXXXXXXXXX?w=400`
7. Los mayoristas del seed deben tener `estado = 'activo'` para aparecer en el marketplace
8. Todas las contraseñas del seed deben hashearse con bcrypt ANTES del INSERT
9. Incluir botón flotante "👁 Ver como tienda" en el panel mayorista para demo rápida
10. El README debe tener tabla con todas las credenciales del seed organizadas por rol

