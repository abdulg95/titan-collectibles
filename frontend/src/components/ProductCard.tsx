type Props = {
    title: string;
    series?: string;
    onBuy?: () => void;
    packImg: string;
    leftCardImg?: string;
    rightCardImg?: string;
    children?: React.ReactNode; // optional description/details
  };

const ASSET_VERSION = '20251202'; // Cache bust version

function addCacheBust(url: string): string {
  if (!url) return url;
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}v=${ASSET_VERSION}`;
}
  
  export default function ProductCard({
    title, series, onBuy, packImg, leftCardImg, rightCardImg, children
  }: Props){
    return (
      <div className="product-card">
        <div className="product-card__media">
          <div className="product-card__stack">
            {leftCardImg && <img className="img img--left" src={addCacheBust(leftCardImg)} alt="" />}
            <img className="img img--pack" src={addCacheBust(packImg)} alt={title} />
            {rightCardImg && <img className="img img--right" src={addCacheBust(rightCardImg)} alt="" />}
          </div>
          <div className="corner-accent" />
        </div>
      </div>
    );
  }
  