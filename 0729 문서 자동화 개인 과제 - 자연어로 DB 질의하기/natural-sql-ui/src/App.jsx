import { useState } from "react";
import axios from "axios";

export default function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    try {
        const res = await axios.post("http://localhost:5000/query", { 
        question 
    });
        console.log(res.data)
        setResult(res.data.result);
    } catch (err) {
        console.error("❌ 요청 실패:", err);         // 추가
        console.error("📡 응답 객체:", err.response); // 추가
        alert("에러 발생: " + err.message);
    }
    setLoading(false);
  };

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">💬 자연어로 DB 질의하기</h1>
      <input
        className="border p-2 w-full mb-4"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="예: 이번 달 가장 많이 팔린 상품은?"
      />
      <button onClick={handleQuery} className="bg-blue-500 text-white px-4 py-2 rounded">
        {loading ? "질의 중..." : "질의 실행"}
      </button>

      {result && (
        <table className="mt-6 border w-full">
          <thead>
            <tr>
              {Object.keys(result[0]).map((key) => (
                <th className="border p-2 bg-gray-100" key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.map((row, idx) => (
              <tr key={idx}>
                {Object.values(row).map((val, i) => (
                  <td className="border p-2" key={i}>{val}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
