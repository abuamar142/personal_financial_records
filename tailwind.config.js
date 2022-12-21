/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./**/*.html"],
    theme: {
      extend: {
        colors: {
          transparent : 'transparent',
          current : 'currentColor',
          primary : '#FFFBEB',
          secondary : '#263159',
        },
      },
    },
    plugins: [],
}