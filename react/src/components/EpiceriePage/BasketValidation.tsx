import React from "react";
import { getCookie } from '../utils/csrf';

interface BasketOrdersProp {
    orders : {
        quantity : number
        basket : {
            id : number
            price : number
            pickup_date : string
        }
    }[]
}

const handleBasketOrderPost = (prop : BasketOrdersProp) => {
    // Formats the orders to the format expected by the backend
    // Send the order to the backend
    // Reload the page
    const orderList = prop.orders.map((order) => {
        return {
            quantity: order.quantity,
            basket_id: order.basket.id
        }
    }
    )

    const data = { baskets : orderList };
    // Upload the order to the backend
    const csrfmiddlewaretoken = getCookie('csrftoken');
    // @ts-ignore Urls is declared in the django template
    fetch(Urls.epicerieBasketOrderList(), {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfmiddlewaretoken,
          },
        body: JSON.stringify(data)
    })
        .then((res) => res.json())
        .then((result) => {
            console.log(result);
            window.location.reload();
        })
        .catch(console.error);
    
    
}

const ConfirmationButton : React.FC<BasketOrdersProp> = (prop : BasketOrdersProp) => {
    // Display the button to confirm the order
    return (
        <div className="epicerie-card-quantity-button">
            <button
                className="button green-button"
                onClick={() => {
                    handleBasketOrderPost(prop);
                }
                }
            >
                Confirmer
            </button>
        </div>
    )
}

const CancelButton : React.FC = () => {
    // Display the button to cancel the order
    return (
        <div className="epicerie-card-quantity-button">
            <button
                className="button red-button"
                onClick={() => {
                    window.location.reload();
                }
                }
            >
                Annuler
            </button>
        </div>
    )
}

export const BasketValidation : React.FC<BasketOrdersProp> = (prop : BasketOrdersProp) => {
    const pluralize = (quantity : number) => {
        // Return the plural or singular form of the word "panier"
        if (quantity > 1) {
            return "paniers"
        } else {
            return "panier"
        }
    }

    const totalPrice = () => {
        // Return the total price of the order
        let total = 0;
        prop.orders.forEach((order) => {
            total += order.quantity * order.basket.price
        }
        )
        return total / 100
    }

    return (
        <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-title">
                    Récapitulatif de ta commande
                </div>
                <div className="epicerie-card-content">
                    <ul>
                        {prop.orders.map((order, index) => {
                            if (order.quantity > 0) {
                                return (
                                    <li key={index}>
                                        <span>
                                            {order.quantity} {pluralize(order.quantity)} à {order.basket.price / 100}€
                                        </span>
                                    </li>
                                )
                            } else {
                                return null
                            }
                        })}
                    </ul>
                </div>
                <div className="epicerie-card-confirmation">
                    <div className="epicerie-card-confirmation-title">
                        Pour un total de : {totalPrice()}€
                    </div>
                    <div className="row">
                        <div className="col">
                            <CancelButton />
                        </div>
                        <div className="col">
                            <ConfirmationButton orders={prop.orders}/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
    };
