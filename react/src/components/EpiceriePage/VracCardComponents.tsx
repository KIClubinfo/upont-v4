import React from "react"

interface QuantityProp {
  quantity : {
    count : number
    increment : () => void
    decrement : () => void
  }
}

interface ProductProp {
    id : number
  name : string
  step : number
  max : number
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

interface Prop extends VracProp, QuantityProp {}

const PrettyComposition : React.FC<VracProp> = (prop : VracProp) => {
  // Display the composition of the basket in a list
  const composition = prop.vrac.ListProducts
  return (
    <div className="epicerie-card-composition">
      <div className="epicerie-vrac-composition-title">
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

const QuantityButtons : React.FC<QuantityProp>  = (prop : QuantityProp) => {
  // Display the quantity of the basket and buttons to increment/decrement it
  // The data is handled in the parent component Basket
  return (
    <div className="epicerie-card-quantity">
      <div className="epicerie-card-quantity-title">
        Quantité :
      </div>
      <div className="epicerie-card-quantity-buttons">
        <button className="button blue-button" onClick={prop.quantity.decrement}>- </button>
        <span className="epicerie-card-quantity-text">{prop.quantity.count}</span>
        <button className="button blue-button" onClick={prop.quantity.increment}> +</button>
      </div>
    </div>
  )
}


export const Vrac: React.FC<Prop> = (prop : Prop) => {
  // Vrac card component
  return (
    <div className="col-sm">
      <div className="epicerie-card">
        <div className="epicerie-card-content">
          <PrettyComposition vrac = {prop.vrac} />
          <QuantityButtons quantity = {prop.quantity}/>
        </div>
      </div>
    </div>
  );
}