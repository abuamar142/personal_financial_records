/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./**/*.html"],
    theme: {
      extend: {
        colors: {
          transparent : 'transparent',
          current : 'currentColor',
          primary : '#F9F5EB',
          secondary : '#25316D',
        },
      },
    },
    plugins: [],
}