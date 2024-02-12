import React from "react";
import { getCookie } from '../utils/csrf';
import { VracOrderPreparingProp } from "./EpicerieProps";

// interface VracOrderPreparingProp {
//     vrac : {
//         id : number
//         quantityList : {
//             id : number
//             name : string
//             price : number
//             quantity : number
//         }[]
//     }
// }

const handleVracOrderPost = (prop : VracOrderPreparingProp) => {
    // Formats the orders to the format expected by the backend
    // Send the order to the backend
    // Reload the page
    const orderList = prop.vracOrder.productQuantities.map((product) => {
        return {
            quantity: product.quantity,
            product_id: product.id
        }
    }
    )

    const data = { 
        vrac_id : prop.vracOrder.vracId,
        listProducts : orderList
    };
    console.log(data)
    // Upload the order to the backend
    const csrfmiddlewaretoken = getCookie('csrftoken');
    // @ts-ignore Urls is declared in the django template
    fetch(Urls.epicerieVracOrderList(), {
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

const ConfirmationButton : React.FC<VracOrderPreparingProp> = (prop : VracOrderPreparingProp) => {
    // Display the button to confirm the order
    return (
        <div className="epicerie-card-quantity-button">
            <button
                className="button green-button"
                onClick={() => {
                    handleVracOrderPost(prop);
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

export const ValidationPage : React.FC<VracOrderPreparingProp> = ( prop : VracOrderPreparingProp ) => {

    const totalPrice = () => {
        let total = 0; // In cents
        prop.vracOrder.productQuantities.forEach((product) => {
            // product price in € / kg and quantity in grams
            total += product.price / 1000 * product.quantity;
        })
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
                        {prop.vracOrder.productQuantities.map((product, index) => {
                            if (product.quantity > 0) {
                                return (
                                    <li key={index}>
                                        <span>
                                            {product.quantity} g de {product.name} ({product.price / 100}€ / kg)
                                        </span>
                                    </li>
                                )
                            } else {
                                return null
                            }
                        })}
                    </ul>
                </div>
                <div className="epicerie-card-button">
                    <div>
                        Total :
                        <br/>
                        {totalPrice()}€
                    </div>
                    <div className="row">
                        <div className="col">
                            <CancelButton />
                        </div>
                        <div className="col">
                            <ConfirmationButton vracOrder={prop.vracOrder}/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}