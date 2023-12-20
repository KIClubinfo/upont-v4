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

const ProductTitle : React.FC<ProductProp> = (prop : ProductProp) => {
  // Display the composition of the basket in a list
  return (
    <div>
      <div className="product-card-title">
        {prop.product.name}
        <br/>
        {prop.product.price / 100}€ / kg
      </div>
    </div>
  )
  }

const QuantityButtons : React.FC<ProductProp>  = (prop : ProductProp) => {
  // Display the quantity of the vrac products and buttons to increment/decrement it
  // The data is handled in the parent component vrac
  return (
    <div className="epicerie-card-quantity">
      <div>
        <button className="button blue-button" onClick={prop.quantity.decrement}>-</button>
        <span >{prop.quantity.count}</span>
        <button className="button blue-button" onClick={prop.quantity.increment}>+</button>
      </div>
    </div>
  )
}

export const Product: React.FC<ProductProp> = (prop : ProductProp) => {
  // Vrac card component
  return (
    <div className="col">
      <div className="product-card">
        <ProductTitle product = {prop.product} quantity={prop.quantity} />
        <QuantityButtons product={prop.product} quantity={prop.quantity} />
      </div>
    </div>
  );
}