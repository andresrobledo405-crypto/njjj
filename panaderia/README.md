# Artesanos Panadería

Sitio estático de una página. Archivos: `index.html`, `styles.css` (Tailwind compilado), `img/` (fotos generadas con IA, referenciales).

## Abrir
Abre `index.html` en cualquier navegador. Las tipografías cargan desde Google Fonts; sin internet se usa una tipografía serif del sistema.

## Publicar para compartir un enlace (sin servidor)
Sube la carpeta `panaderia` completa a uno de estos servicios y comparte la URL que te den:
- **Netlify Drop** (app.netlify.com/drop): arrastra la carpeta.
- **Cloudflare Pages** o **Vercel**: conecta este repositorio y define `panaderia` como directorio raíz, sin comando de build.
- **GitHub Pages**: solo publica la raíz del repositorio o `/docs`, así que copia el contenido de `panaderia` a una de esas rutas.

## Regenerar el CSS
Si cambias clases de Tailwind en `index.html`:
`npx tailwindcss@3.4.17 -i input.css -o styles.css --minify`, con un `input.css` que contenga las tres directivas `@tailwind base; @tailwind components; @tailwind utilities;`.
