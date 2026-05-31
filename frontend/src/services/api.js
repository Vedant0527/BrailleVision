import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const translateBraille = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(
    `${API_URL}/translate/`,
    formData
  );

  return response.data;
};