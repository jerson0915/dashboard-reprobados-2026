# Prompt para pegar en Claude (VS Code)

1. Descomprime `dashboard-reprobados-2026.zip`.
2. En VS Code: **Archivo → Abrir carpeta…** → elige la carpeta `dashboard-reprobados-2026`.
3. Abre Claude en VS Code y pega este texto completo:

---

Estoy en la carpeta del proyecto `dashboard-reprobados-2026`. Súbelo a GitHub. Explícame cada paso porque soy principiante.

1. Verifica que tengo `git` y la CLI de GitHub (`gh`). Si falta alguna, dime cómo instalarla en Mac (con Homebrew) y espera a que te confirme.
2. Verifica que estoy autenticado con `gh auth status`. Si no lo estoy, guíame con `gh auth login`.
3. Inicializa el repositorio con la rama `main`. Revisa el `.gitignore` y haz el primer commit con el mensaje: "Dashboard de reprobación secundaria 2026".
4. Crea el repositorio en GitHub como **PRIVADO** (`gh repo create dashboard-reprobados-2026 --private --source=. --push`). Contiene nombres de estudiantes menores de edad: bajo ninguna circunstancia lo crees público ni actives GitHub Pages.
5. Al terminar, muéstrame la URL del repositorio y confirma que dice "Private".
6. Opcional (pregúntame antes): si quiero invitar a alguien del comité, usa `gh api` para agregarlo como colaborador con el usuario de GitHub que yo te dé.

---

## Si después quieres una versión pública (página web)

Publica **solo** `index_anonimo.html`, que no tiene nombres, y desde un repositorio **aparte**. No actives GitHub Pages en este repositorio privado, porque también contiene el Excel y `index.html` con nombres.
