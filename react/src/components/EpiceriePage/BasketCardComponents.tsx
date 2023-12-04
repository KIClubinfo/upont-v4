import React from "react"

interface QuantityProp {
  quantity : {
    count : number
    increment : () => void
    decrement : () => void
  }
}

interface BasketProp {
  basket :{
    id : number
    price : number
    composition : string[]
    open_date : string
    close_date : string
    pickup_date : string
  },
}

interface Prop extends BasketProp, QuantityProp {}

const BasketPrice : React.FC<BasketProp> = (prop : BasketProp) => {
  // Display the price of the basket
  const price = prop.basket.price
  return (
    <div className="epicerie-card-title">
      <span>
        Panier à {price / 100}€
      </span>
    </div>
  )
}

const PrettyComposition : React.FC<BasketProp> = (prop : BasketProp) => {
  // Display the composition of the basket in a list
  const composition = prop.basket.composition
  return (
    <div className="epicerie-card-composition">
      <div className="epicerie-basket-composition-title">
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


export const Basket: React.FC<Prop> = (prop : Prop) => {
  // Basket card component
  return (
    <div className="col-sm">
      <div className="epicerie-card">
        <BasketPrice basket = {prop.basket} />
        <div className="epicerie-card-content">
          <PrettyComposition basket = {prop.basket} />
          <QuantityButtons quantity = {prop.quantity}/>
        </div>
      </div>
    </div>
  );
}