import React, { useState } from "react";
import Skill_Input from "./Skill_Input";
import Domain from "./Domain";
import { ClipboardList } from "lucide-react";
import data from "./categories.json";
import Experience from "./Experience";

function SkillAssessment() {
  const [option, setOption] = useState("");

  return (
    <div className="bg-[#F7F7F7] pt-32 pb-10 px-20 ">
      <div className="mb-6 flex items-center">
        <ClipboardList className="w-10 h-9 text-[#18BED4]" />
        <h2 className="text-3xl font-bold text-[#1F2833]">Skill Assessment</h2>
      </div>
      <form className="p-4 bg-white shadow-lg rounded-2xl" action="">
        <div className=" text-[#1F2833] text-start grid grid-cols-2 gap-5">
          <Domain
            options={Object.keys(data)}
            label="Select Your Domain"
            className=""
            option
            setOption={setOption}
          />
          <Experience
            label="Experience (in years)"
            className=""
            option
            setOption={setOption}
          />
        </div>
        <div className="grid grid-cols-2 gap-5">
          {[...Array(8)].map((_, index) => (
            <Skill_Input
              key={index}
              value={data[option]?.[index] || ""} // Assign the skill value or empty string if not available
              index={index + 1}
              disabled={!option} // Disable if no domain is selected
            />
          ))}
        </div>
        <button
          type="submit"
          disabled={!option}
          className="w-full mt-8 px-4 py-2 rounded-lg bg-[#18BED4] hover:bg-[#15a8bc]"
        >
          Submit
        </button>
      </form>
    </div>
  );
}

export default SkillAssessment;
