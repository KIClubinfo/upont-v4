import React from "react"

interface ProductProp {
  id : number
  name : string
  step : number
  max : number
  quantity : {
    count : number
    increment : (event : Event, step : number) => void
    decrement : (event : Event, step : number) => void
  }
  price : number
}

interface VracProp {
  vrac :{
    id : number
    ListProducts : ProductProp[]
    open_date : string
    close_date : string
    pickup_date : string
  },
}

interface Prop extends VracProp {}

const PrettyComposition : React.FC<VracProp> = (prop : VracProp) => {
  // Display the composition of the basket in a list
  const composition = prop.vrac.ListProducts
  return (
    <div className="vrac-card-composition">
      <div className="vrac-composition-title">
        Composition :
        </div>
      <br></br>
      <ul>
        {composition.map((line, index) => (
          <li key={index}>{line}</li>
        ))}
      </ul>
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

export const Vrac: React.FC<Prop> = (prop : Prop) => {
  // Vrac card component
  return (
    <div className="col-sm">
      <div className="vrac-card">
        <div className="vrac-card-content">
          <PrettyComposition vrac = {prop.vrac} />
        </div>
      </div>
    </div>
  );
}