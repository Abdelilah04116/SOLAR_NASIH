import { IonIcon } from "@ionic/react";
import { sparkles } from "ionicons/icons";
import { useSettings } from "../../store/store";
import classNames from "classnames";

export default function GptIntro() {
  return (
    <>
      {/* Removed modals selection div */}
      <div className="h-96 flex items-start justify-center">
        <h1 className="text-4xl font-bold mt-5 text-center text-gray-300">
          SolarNasih
        </h1>
      </div>
    </>
  );
}