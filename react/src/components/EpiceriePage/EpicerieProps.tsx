export interface VracOrderProp {
    vracOrder : {
        id : number,
        student :{
            id : number,
            first_name : string,
            last_name : string,
            email : string,
            phone : string,
        },
        vrac : {
            id : number,
            pickup_date : string
        },
        order : [
            {
                id : number,
                product : string,
                quantity : number
            }
        ],
        total : number,
        
    }
}

export interface VracOrderPreparingProp {
    vracOrder : {
        vracId : number
        productQuantities : {
            id : number
            name : string
            price : number
            quantity : number
        }[]
    }
}

export interface VracProp {
    vrac : {
        id : number
        pickup_date : string
        ListProducts : {
            id : number
            name : string
            price : number
            step : number
            max : number
        }[]
    }
}

export interface QuantityProp {
    quantity : {
      count : number
      increment : () => void
      decrement : () => void
    }
  }

export interface Vegetable {
    id : number
    name : string
    quantity : number
}
  
export interface BasketProp {
    basket :{
      id : number
      price : number
      composition : Vegetable[]
      open_date : string
      close_date : string
      pickup_date : string
    },
  }
  
export interface BasketCardProp extends BasketProp, QuantityProp {}