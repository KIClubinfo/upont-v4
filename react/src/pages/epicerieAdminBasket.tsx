import { render } from 'react-dom';
import AdminBasket from '../components/EpiceriePage/AdminBasket';

// @ts-ignore window.react_mount is declared in django template
render(<AdminBasket />, window.react_mount);