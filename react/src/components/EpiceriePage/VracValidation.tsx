import React from "react";
import { getCookie } from '../utils/csrf';

interface OrdersProp {
    vrac : {
        id : number
        ListProducts : {
            id : number
            name : string
            price : number
            quantity : number
        }[]
    }
}

export const ValidationPage : React.FC= () => {
    return (
        <div>
            Coucou
        </div>
    )
}