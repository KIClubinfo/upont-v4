import React from "react";
import { useState , useEffect} from "react";

interface sethasOrderedProp {
    sethasOrdered: (hasOrdered: boolean) => void
}


export const ExistingOrder: React.FC<sethasOrderedProp> = (prop : sethasOrderedProp) => {

    const [orders, setOrders ] = useState([
        {
            order : [
                {
                    product : "",
                    quantity : 0
                }
            ],
            total : 0,
            vrac : {
                pickup_date : ""
            }
        }
    ]
    )

    const getOrders = () =>
        // @ts-ignore Urls is declared in the django template
        fetch(Urls.epicerieVracOrderList())
        .then((res) => res.json())
        .then((result) => {
            setOrders(result.results)
        })
        .catch(console.error);

    useEffect(() => {
        getOrders();
    }
    , []);

    console.log(orders)

    return (
        <div className="row row-cols-5">
            {orders.map((vrac, index) => {
                return (
                    <div className="col-sm" key={index}>
                        <div className="epicerie-card">
                            <div className="epicerie-card-title">
                                Tu as déjà commandé un panier !
                                <br/>
                                Récapitulatif de ta commande :
                            </div>
                            <div className="epicerie-card-content">
                                {
                                vrac.order.map((product, subindex) => {
                                    return (
                                        <li key={subindex}>
                                            {product.product} : {product.quantity}
                                        </li>
                                    )})
                                }   
                            </div>
                            <div className="epicerie-card-button">
                                <div>
                                    Pour un total des :
                                </div>
                                <div>
                                    {vrac.total / 100}€
                                </div>
                                <button className="button green-button"
                                onClick={() => {
                                    prop.sethasOrdered(false)
                                }}>
                                    Commander à nouveau
                                </button>
                            </div>
                        </div>
                        
                    </div>
                )
                }
            )}
        </div>

    )
}