# 📦 Yiwu Lists 


### ✅ Autenticación
- Registro con nombre, email y contraseña (bcrypt)
- Login con JWT (token guardado en cookie 7 días)
- Logout
- Protección de rutas (redirige a /login si no autenticado)

### ✅ Gestión de listas
- Crear lista con nombre y descripción
- Ver todas tus listas con contador de productos
- Editar nombre y descripción
- Eliminar lista (elimina también todos sus productos)

### ✅ Gestión de productos
- Agregar producto con:
  - 📷 Foto (upload desde móvil/cámara o archivo)
  - Nombre y referencia
  - Precio en USD
  - Medidas: ancho, alto, profundidad (cm)
  - Peso (kg)
  - Nombre y número de tienda
  - Notas libres
- Editar cualquier campo del producto
- Eliminar producto (con confirmación)

### ✅ Export a Excel
- Exporta lista completa a .xlsx
- Incluye las fotos de los productos en las celdas
- Formato profesional con colores, bordes y número format para precios
- Descarga directa desde el navegador