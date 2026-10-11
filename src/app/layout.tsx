import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Calculadoras de Enfermagem',
  description: 'Plataforma clínica de calculadoras, escalas e recursos baseados em evidências.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  )
}
