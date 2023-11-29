import React from "react"

interface BasketProp {
  basket :{
    id : number
    price : number
    composition : string
    open_date : string
    close_date : string
    pickup_date : string
  }
}

const BasketPrice : React.FC<BasketProp> = (prop : BasketProp) => {
  const price = prop.basket.price
  return (
    <div className="epicerie-card-price">
      <span className="epicerie-card-price-text">
        Panier à {price / 100}€
      </span>
    </div>
  )
}

const PrettyComposition : React.FC<BasketProp> = (prop : BasketProp) => {
  const composition = prop.basket.composition
  return (
    <div className="epicerie-card-composition">
      <div className="epicerie-basket-composition-title">
        Composition :
        </div>
      <br></br>
      <ul>
        {composition.split("\n").map((line) => (
          <li>{line}</li>
        ))}
      </ul>
    </div>
  )
}

export const Basket: React.FC<BasketProp> = (prop : BasketProp) => (
    <div className="col-sm">
      <div className="epicerie-card">
        <div className="epicerie-card-content">
          <BasketPrice basket = {prop.basket}/>
          <PrettyComposition basket = {prop.basket}/>
        </div>
      </div>
    </div>
);