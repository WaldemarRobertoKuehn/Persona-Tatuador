# Usa Node para instalar as dependências e gerar os arquivos estáticos.
FROM node:22 AS build

# Define a pasta de trabalho da etapa de build.
WORKDIR /app

# Copia os manifestos para instalar as versões registradas no lockfile.
COPY package.json package-lock.json ./

# Instala exatamente as dependências registradas no package-lock.json.
RUN npm ci

# Copia o código do frontend para a etapa de build.
COPY . .

# Gera os arquivos estáticos de produção.
RUN npm run build

# Usa Caddy para servir os arquivos estáticos gerados.
FROM caddy:2

# Copia o resultado do build para a pasta servida pelo Caddy.
COPY --from=build /app/dist/ /srv/
