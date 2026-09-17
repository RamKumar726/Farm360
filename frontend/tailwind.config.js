/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      opacity: {
        '3': '0.03',
        '8': '0.08',
        '15': '0.15',
      },
      colors: {
        primary: {
          DEFAULT: "#1a3c2e",
          50: "#f0f7f3",
          100: "#d5ead8",
          200: "#abd6b6",
          300: "#75b88a",
          400: "#48986a",
          500: "#2e7a52",
          600: "#1a3c2e",
          700: "#163326",
          800: "#11291e",
          900: "#0a1a12",
        },
        accent: {
          DEFAULT: "#c9a84c",
          50: "#fdf9ee",
          100: "#f9efcf",
          200: "#f2dc9a",
          300: "#e9c55f",
          400: "#c9a84c",
          500: "#b08932",
          600: "#8f6a22",
          700: "#6f4f1a",
          800: "#4f3714",
          900: "#33230d",
        },
        surface: "#1e4535",
        background: "#0f1f19",
        muted: "#2a5540",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Outfit", "sans-serif"],
      },
      backgroundImage: {
        "hero-gradient": "linear-gradient(135deg, #1a3c2e 0%, #0f1f19 100%)",
        "card-gradient": "linear-gradient(145deg, rgba(30,69,53,0.8) 0%, rgba(15,31,25,0.9) 100%)",
        "gold-gradient": "linear-gradient(135deg, #c9a84c 0%, #e9c55f 50%, #c9a84c 100%)",
      },
      boxShadow: {
        "card": "0 4px 24px rgba(0,0,0,0.4), 0 1px 4px rgba(0,0,0,0.3)",
        "glow": "0 0 20px rgba(201,168,76,0.3)",
        "glow-green": "0 0 20px rgba(26,60,46,0.5)",
      },
      animation: {
        "fade-in": "fadeIn 0.4s ease-out",
        "slide-up": "slideUp 0.4s ease-out",
        "pulse-slow": "pulse 3s ease-in-out infinite",
        "shimmer": "shimmer 2s infinite",
      },
      keyframes: {
        fadeIn: { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: "translateY(16px)" }, to: { opacity: 1, transform: "translateY(0)" } },
        shimmer: { "0%": { backgroundPosition: "-200% 0" }, "100%": { backgroundPosition: "200% 0" } },
      },
    },
  },
  plugins: [],
};
