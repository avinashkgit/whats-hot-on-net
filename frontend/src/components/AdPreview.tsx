export function AdPreview({ label = "AdSense Ad Preview" }: { label?: string }) {
  return (
    <div className="w-full flex justify-center">
      <div className="w-full max-w-4xl border border-dashed border-border rounded-2xl bg-muted/40 p-6 text-center">
        <p className="text-sm font-semibold text-muted-foreground">{label}</p>
        <p className="text-xs text-muted-foreground mt-1">
          This is only a preview placeholder. Real ads will appear here.
        </p>

        <div className="mt-4 h-[120px] w-full rounded-xl bg-background/60 border border-border flex items-center justify-center">
          <span className="text-xs text-muted-foreground">
            Responsive Ad Area
          </span>
        </div>
      </div>
    </div>
  );
}
