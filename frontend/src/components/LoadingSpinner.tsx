/* LoadingSpinner: simple spinning loader */
export default function LoadingSpinner({ size = 40 }: { size?: number }) {
  return (
    <div className="spinner-container">
      <div className="spinner" style={{ width: size, height: size }} />
    </div>
  );
}
