import { CompositionPreview } from '@/components/builder/CompositionPreview'
import example from '../../../packages/builder/example_composition.json'

export default function BuilderPage() {
  return (
    <main style={{ padding: '2rem' }}>
      <h1>Builder Canônico — Preview</h1>
      <p>Composição de exemplo usando tokens oficiais. Camadas são opcionais.</p>
      <CompositionPreview composition={example as any} />
      <pre style={{ marginTop: '1rem', fontSize: 12, background: '#F8FAFC', padding: 16 }}>
        {JSON.stringify(example, null, 2)}
      </pre>
    </main>
  )
}
