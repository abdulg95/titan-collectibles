type Props = {
    title: string;
    series?: string;
    onBuy?: () => void;
    packImg: string;
    leftCardImg?: string;
    rightCardImg?: string;
    children?: React.ReactNode; // optional description/details
  };
  
  export default function ProductCard({
    title, series, onBuy, packImg, leftCardImg, rightCardImg, children
  }: Props){
    return (
      <div className="product-card">
        <div className="product-card__media">
          <div className="product-card__stack">
            {leftCardImg && <img className="img img--left" src={leftCardImg} alt="" />}
            <img className="img img--pack" src={packImg} alt={title} />
            {rightCardImg && <img className="img img--right" src={rightCardImg} alt="" />}
          </div>
          <div className="corner-accent" />
        </div>
      </div>
    );
  }
  