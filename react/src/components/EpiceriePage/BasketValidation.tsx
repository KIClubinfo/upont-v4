import React from "react";
import { getCookie } from '../utils/csrf';

interface OrdersProp {
    orders : {
        quantity : number
        basket : {
            id : number
            price : number
            pickup_date : string
        }
    }[]
}

const handleOrderPost = (prop : OrdersProp) => {
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

const ConfirmationButton : React.FC<OrdersProp> = (prop : OrdersProp) => {
    // Display the button to confirm the order
    return (
        <div className="epicerie-card-quantity-button">
            <button
                className="btn btn-primary"
                onClick={() => {
                    handleOrderPost(prop);
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
                className="btn btn-primary"
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

export const BasketValidation : React.FC<OrdersProp> = (prop : OrdersProp) => {
    return (
        <div>
        <h1>Recapitulatif de la commande</h1>
        <ul>
            {prop.orders.map((order, index) => (
                <li key={index}>
                    {order.quantity} paniers à {order.basket.price / 100}€
                </li>
            ))}
        </ul>
        <ConfirmationButton orders = {prop.orders} />
        <CancelButton />
        </div>
    );
    };
