## ADDED Requirements

### Requirement: Next.js 15 App Router inicializado
La aplicación frontend SHALL usar Next.js 15 con App Router. El directorio de rutas SHALL ser `src/app/`. TypeScript SHALL configurarse en modo estricto.

#### Scenario: Aplicación compila sin errores
- **WHEN** se ejecuta `npm run build` en `/frontend`
- **THEN** el build termina sin errores de compilación TypeScript

#### Scenario: Página raíz accesible
- **WHEN** se accede a `http://localhost:3000` con el servidor corriendo
- **THEN** la respuesta es HTTP 200
- **THEN** el HTML contiene un documento válido con la estructura base del proyecto

### Requirement: Tailwind CSS 4 configurado
El proyecto SHALL usar Tailwind CSS 4 con configuración básica. Los estilos globales SHALL importarse en el layout raíz (`src/app/layout.tsx`).

#### Scenario: Clases de Tailwind aplicadas correctamente
- **WHEN** se añade una clase de Tailwind a un componente
- **THEN** el estilo se aplica correctamente en el navegador sin configuración adicional

### Requirement: shadcn/ui inicializado
El proyecto SHALL tener shadcn/ui inicializado con al menos un componente base instalado (Button). La configuración SHALL estar en `components.json`. Los componentes SHALL residir en `src/components/ui/`.

#### Scenario: Componente Button importable
- **WHEN** se importa `Button` desde `@/components/ui/button`
- **THEN** la importación resuelve sin errores de TypeScript

### Requirement: Zustand store base configurado
SHALL existir al menos un store base de Zustand en `src/store/`. La configuración SHALL soportar devtools en desarrollo.

#### Scenario: Store importable y funcional
- **WHEN** se importa el store desde `src/store/`
- **THEN** el store inicializa sin errores

### Requirement: Cliente HTTP configurado
SHALL existir un cliente HTTP centralizado en `src/lib/api-client.ts` que configure la base URL del API desde variables de entorno (`NEXT_PUBLIC_API_URL`). Este cliente SHALL ser el único punto de comunicación con el backend.

#### Scenario: Cliente HTTP usa la URL del entorno
- **WHEN** la variable `NEXT_PUBLIC_API_URL` está definida
- **THEN** todas las peticiones HTTP se envían a esa base URL

### Requirement: Metadatos globales configurados
El layout raíz SHALL definir metadatos base (`title`, `description`) usando la API de metadatos de Next.js 15. Cada página deberá poder sobreescribir estos metadatos.

#### Scenario: Metadatos base presentes en el HTML
- **WHEN** se solicita cualquier página de la aplicación
- **THEN** el HTML resultante contiene `<title>` y `<meta name="description">` con valores no vacíos
