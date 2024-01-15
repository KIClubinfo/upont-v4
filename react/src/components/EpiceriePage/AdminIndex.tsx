import React from "react";

const ImportBasketCard : React.FC = () => {

    return (
        <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-title">Importer le nouveau vrac </div>
                <div className="epicerie-card-content">
                <form encType="multipart/form-data" action="/api/epicerie/baskets/" method="POST">
                    <button type="button" className="button blue-button" id="upload-button"> Choisir un fichier</button>
                    <input type="date" className="button blue-button" id="date-open"> Date d'ouverture des commandes </input>
                    <input type="date" className="button blue-button" id="date-close"> Date de fermeture des commandes </input>
                    <input type="date" className="button blue-button" id="date-pickup"> Date de récupération </input>
                    <input type="submit" className="button blue-button" value="Upload File" />
                </form>
                </div>
                
            </div>
        </div>
    )

}

const Admin = () => {

    return (
        <div className="row row-cols-3">
            <div className="col-sm">
                <div className="epicerie-card">
                    <div className="epicerie-card-content">
                        <div className="row">
                            <button className="button blue-button">
                                <a href="/api/epicerie/basket_orders/export" target="_blank" rel="noopener noreferrer">
                                    Exporter les commandes de paniers
                                </a>
                            </button>
                        </div>
                        <div className="row">
                            <button className="button blue-button">
                                <a href="/api/epicerie/vrac_orders/export" target="_blank" rel="noopener noreferrer">
                                    Exporter les commandes de vrac
                                </a>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="col-sm">
            <div className="epicerie-card">
                <div className="epicerie-card-title">Importer le nouveau vrac </div>
                <div className="epicerie-card-content">
                <form encType="multipart/form-data" action="/api/epicerie/baskets/" method="POST">
                    <button type="button" className="button blue-button" id="upload-button"> Choisir un fichier</button>
                    <input type="date" className="button blue-button" id="date-open"> Date d'ouverture des commandes </input>
                    <input type="date" className="button blue-button" id="date-close"> Date de fermeture des commandes </input>
                    <input type="date" className="button blue-button" id="date-pickup"> Date de récupération </input>
                    <input type="submit" className="button blue-button" value="Upload File" />
                </form>
                </div>
                
            </div>
        </div>

        </div>
    );
    }

export default Admin;