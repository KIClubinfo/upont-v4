import { render } from 'react-dom';
import Baskets from '../components/EpiceriePage/BasketsComponents';

// @ts-ignore window.react_mount is declared in django template
render(<Baskets />, window.react_mount);
