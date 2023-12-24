import React from "react";
import { VracOrderPreparingProp } from "./EpicerieProps";
import { getCookie } from '../utils/csrf';

export const DeletionPage : React.FC<VracOrderPreparingProp> = ( prop : VracOrderPreparingProp ) => {

    const handleCancel  = () => {
        window.location.reload();
    }

    const handleDelete = () => {
        let data = {
            vracId : prop.vracOrder.vracId
        }
        // @ts-ignore Urls is declared in the django template
        fetch (Urls.epicerieVracOrderDeleteVracOrder(), {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
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

    return (
        <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-title">
                    Tu t'apprêtes à supprimer ta commande.
                    <br/>
                    Es-tu-sûr ?
                </div>
                <div className="epicerie-card-content">
                    Récapitulatif de ta commmande :
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
                    <div className="row">
                        <div className="col">
                            <button className="button green-button"
                            onClick={handleCancel}>
                                Annuler
                            </button>
                        </div>
                        <div className="col">
                            <button className="button red-button"
                            onClick={handleDelete}>
                                Supprimer
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    )
}