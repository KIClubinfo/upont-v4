import React from "react"

interface ProductProp {
  product : {
    name : string
    price : number
  }
  quantity : {
    count : number
    increment : () => void
    decrement : () => void
  }
}

const PrettyComposition : React.FC<ProductProp> = (prop : ProductProp) => {
  // Display the composition of the basket in a list
  return (
    <div className="vrac-card-composition">
      <div className="vrac-card-composition-title">
        {prop.product.name} : {prop.product.price / 100}€
      </div>
    </div>
  )
}

const QuantityButtons : React.FC<ProductProp>  = (prop : ProductProp) => {
  // Display the quantity of the vrac products and buttons to increment/decrement it
  // The data is handled in the parent component vrac
  return (
    <div className="vrac-card-quantity">
      <div className="vrac-card-quantity-title">
        Quantité :
      </div>
      <div className="vrac-card-quantity-buttons">
        <button className="button blue-button" onClick={prop.quantity.decrement}>- </button>
        <span className="vrac-card-quantity-text">{prop.quantity.count}</span>
        <button className="button blue-button" onClick={prop.quantity.increment}> +</button>
      </div>
    </div>
  )
}

export const Product: React.FC<ProductProp> = (prop : ProductProp) => {
  // Vrac card component
  return (
    <div className="col-sm">
      <div className="vrac-card">
        <div className="vrac-card-content">
          <PrettyComposition product={prop.product} quantity={prop.quantity} />
        </div>
        <QuantityButtons product={prop.product} quantity={prop.quantity} />
      </div>
    </div>
  );
}