import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/";

export const getUsers = () => {
  const { getAccessTokenSilently } = useAuth0();
  const url = `${BASE_URL}getUsers`;

  const fetchData = async () => {
    const token = await getAccessTokenSilently();
    const response = await axios.get(url, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  };

  return { fetchData };
};
