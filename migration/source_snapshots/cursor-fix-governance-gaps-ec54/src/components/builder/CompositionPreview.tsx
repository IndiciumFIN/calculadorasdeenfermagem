import tokens from '../../../packages/design-system/tokens.json';

type Layer = {
  id: string;
  type: string;
  variant?: string;
  locked?: boolean;
  editable?: boolean;
};

type Composition = {
  id: string;
  canvas: { width: number; height: number };
  layers: Layer[];
};

export function CompositionPreview({ composition }: { composition: Composition }) {
  return (
    <div
      style={{
        width: composition.canvas.width / 4,
        height: composition.canvas.height / 4,
        background: tokens.colors.background,
        border: `1px solid ${tokens.colors.primary}`,
        position: 'relative',
        fontFamily: tokens.typography.font_family,
      }}
    >
      {composition.layers.map((layer) => (
        <div key={layer.id} style={{ padding: 8, fontSize: 12 }}>
          {layer.id} ({layer.type})
        </div>
      ))}
    </div>
  );
}
