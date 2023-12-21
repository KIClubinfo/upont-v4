import React from "react";
import { VracOrderProp } from "./EpicerieProps";

interface sethasOrderedProp {
    sethasOrdered: (hasOrdered: boolean) => void
}

interface ExistingOrderProp extends sethasOrderedProp, VracOrderProp {}

export const ExistingOrder: React.FC<ExistingOrderProp> = (prop : ExistingOrderProp) => {

    return (
        <div className="row row-cols-5">
            <div className="epicerie-card">
                <div className="epicerie-card-title">
                    Tu as déjà commandé un panier !
                    <br/>
                    Récapitulatif de ta commande :
                </div>
                <div className="epicerie-card-content">
                    {
                    prop.vracOrder.order.map((product, subindex) => {
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
                        {prop.vracOrder.total / 100}€
                    </div>
                    <button className="button green-button"
                    onClick={() => {
                        prop.sethasOrdered(false)
                    }}>
                        Modifier ma commande
                    </button>
                </div>
            </div>
        </div>

    )
}