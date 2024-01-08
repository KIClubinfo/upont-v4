import React from "react";

const ExportBasketOrders = () => {

}

const Admin = () => {
    return (
        <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-content">
                    <div className="row">
                        <button className="button blue-button">
                            Modifier les paniers
                        </button>
                    </div>
                    <div className="row">
                        <button className="button blue-button">
                            Modifier le vrac
                        </button>
                    </div>
                    <div className="row">
                        <button className="button blue-button"
                        onClick={ExportBasketOrders}>
                            Exporter les commandes de paniers
                        </button>
                    </div>
                    <div className="row">
                        <button className="button blue-button">
                            Exporter les commandes de vrac
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
    }

export default Admin;