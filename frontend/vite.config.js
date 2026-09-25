import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],

  /* publicDir diz ao Vite de onde ele pega os arquivos que são servidos como
   * estão, sem passar por build, e que o index.html pode pedir por caminho.
   *
   * Aqui ele aponta para docs/marca, e a razão é não duplicar a marca. Os SVG do
   * logotipo já estão em docs/marca/, que é onde a REGRAS manda que fiquem, e o
   * front precisa deles. Copiar para o public/ do front daria dois arquivos
   * iguales no Git, e no dia em que a linha do logo mudasse de espessura o
   * arquivo do front continuaria com a linha velha, sem ninguém perceber.
   *
   * Apontar para a pasta de origem faz o servidor do Vite e o build entregarem o
   * mesmo arquivo que está versionado, e a interface não tem cópia nenhuma.
   */
  publicDir: '../docs/marca',
})
