import React, {useState, useEffect} from "react";


export const DisplayExistingOrder : React.FC = () => {
    // Display the existing order of the user
    const [orders, setOrders] = useState([]);
    // Get the orders of the user
    const getOrders = () =>
    // @ts-ignore Urls is declared in the django template
        fetch(Urls.epicerieBasketOrderList())
            .then((res) => res.json())
            .then((result) => {
                setOrders(result.results)
            })
            .catch(console.error);

    useEffect(() => {
        getOrders();
    }
    , []);

    const pluralize = (quantity : number) => {
        // Return the plural or singular form of the word "panier"
        if (quantity > 1) {
            return "paniers"
        } else {
            return "panier"
        }
    }

    return (
        <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-title">
                    Vos commandes :
                </div>
                <div className="epicerie-card-content">
                    <ul>
                        {
                        orders.map(
                            (order, index) => (
                            <li key={index}>
                                {order.quantity} {pluralize(order.quantity)} à {order.basket.price / 100}€
                            </li>)
                            )
                        }
                    </ul>
                </div>
            </div>
        </div>
    )
}