import { render } from 'react-dom';
import { Basket_order } from '../components/EpiceriePage/BasketComponents';

// @ts-ignore window.react_mount is declared in django template
render(<Basket_order />, window.react_mount);
